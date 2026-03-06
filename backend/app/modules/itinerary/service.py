from collections import defaultdict
from sqlalchemy.orm import Session

from db.models.catalog_item import CatalogItem
from db.models.group import Group
from db.models.itinerary import Itinerary
from db.models.itinerary_day import ItineraryDay
from db.models.itinerary_item import ItineraryItem
from db.models.membership import Membership
from db.models.preference import Preference
from db.models.vote import Vote
from db.models.notification import Notification


def _require_active_membership(db: Session, group_id: int, user_id: int) -> Membership:
    membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == user_id,
        Membership.status == "ACTIVE",
    ).first()
    if not membership:
        raise ValueError("FORBIDDEN")
    return membership


def _latest_itinerary(db: Session, group_id: int) -> Itinerary | None:
    return db.query(Itinerary).filter(Itinerary.group_id == group_id).order_by(Itinerary.id.desc()).first()


def _serialize_itinerary(db: Session, itinerary: Itinerary):
    days = db.query(ItineraryDay).filter(ItineraryDay.itinerary_id == itinerary.id).order_by(ItineraryDay.day_number.asc()).all()
    items = db.query(ItineraryItem).join(ItineraryDay, ItineraryItem.itinerary_day_id == ItineraryDay.id).filter(
        ItineraryDay.itinerary_id == itinerary.id
    ).all()
    items_by_day = defaultdict(list)
    for item in items:
        items_by_day[item.itinerary_day_id].append(item)

    day_rows = []
    for day in days:
        day_rows.append(
            {
                "day_number": day.day_number,
                "items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "summary": item.summary,
                        "estimated_cost": item.estimated_cost,
                        "duration_hours": float(item.duration_hours),
                        "rationale": item.rationale,
                    }
                    for item in items_by_day[day.id]
                ],
            }
        )
    approve_count = db.query(Vote).filter(Vote.itinerary_id == itinerary.id, Vote.value == "APPROVE").count()
    changes_count = db.query(Vote).filter(Vote.itinerary_id == itinerary.id, Vote.value == "CHANGES").count()
    total_votes = approve_count + changes_count

    return {
        "id": itinerary.id,
        "group_id": itinerary.group_id,
        "state": itinerary.state,
        "confidence_score": itinerary.confidence_score,
        "created_by": itinerary.created_by,
        "created_at": itinerary.created_at,
        "vote_summary": {
            "approve": approve_count,
            "changes": changes_count,
            "total": total_votes,
        },
        "days": day_rows,
    }


def get_group_itinerary(db: Session, group_id: int, user_id: int):
    _require_active_membership(db, group_id, user_id)
    itinerary = _latest_itinerary(db, group_id)
    if not itinerary:
        raise ValueError("ITINERARY_NOT_FOUND")
    return _serialize_itinerary(db, itinerary)


def generate_itinerary(db: Session, group_id: int, user_id: int):
    _require_active_membership(db, group_id, user_id)
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("GROUP_NOT_FOUND")

    current = _latest_itinerary(db, group_id)
    if current and current.state in {"REVIEW", "LOCKED"}:
        raise ValueError("INVALID_STATE")

    prefs = db.query(Preference).filter(Preference.group_id == group_id).all()
    days = max(1, min(7, int(sum([p.days for p in prefs if p.days is not None]) / max(len([p for p in prefs if p.days is not None]), 1)) if any(p.days is not None for p in prefs) else 3))
    budget_max_values = [p.budget_max for p in prefs if p.budget_max is not None]
    budget_cap = int(sum(budget_max_values) / max(len(budget_max_values), 1)) if budget_max_values else 100

    interests = set()
    for p in prefs:
        interests.update(p.activities or [])

    candidates = db.query(CatalogItem).all()
    if not candidates:
        raise ValueError("CATALOG_EMPTY")

    scored = []
    for item in candidates:
        tags = {tag.strip() for tag in (item.tags_csv or "").split(",") if tag.strip()}
        interest_match = len(interests.intersection(tags))
        budget_penalty = max(0, item.estimated_budget - budget_cap)
        score = (interest_match * 20) + max(0, 100 - budget_penalty)
        scored.append((score, item, interest_match, budget_penalty))
    scored.sort(key=lambda x: x[0], reverse=True)

    selected = [row[1] for row in scored[: max(days, 2)]]
    confidence = int(sum([row[0] for row in scored[: min(len(scored), days)]]) / max(min(len(scored), days), 1))
    confidence = max(0, min(100, confidence))

    itinerary = Itinerary(group_id=group_id, state="DRAFT", confidence_score=confidence, created_by=user_id)
    db.add(itinerary)
    db.flush()

    for i in range(days):
        day = ItineraryDay(itinerary_id=itinerary.id, day_number=i + 1)
        db.add(day)
        db.flush()
        item = selected[i % len(selected)]
        tags = [tag.strip() for tag in (item.tags_csv or "").split(",") if tag.strip()]
        rationale = f"Matched {min(len(interests.intersection(set(tags))), 3)} shared interests and fits budget band."
        db.add(
            ItineraryItem(
                itinerary_day_id=day.id,
                title=item.title,
                summary=item.summary,
                estimated_cost=item.estimated_budget,
                duration_hours=item.duration_hours,
                rationale=rationale,
            )
        )

    members = db.query(Membership).filter(Membership.group_id == group_id, Membership.status == "ACTIVE").all()
    for member in members:
        db.add(
            Notification(
                user_id=member.user_id,
                group_id=group_id,
                kind="ITINERARY_GENERATED",
                message=f'New itinerary draft generated for "{group.name}".',
            )
        )

    db.commit()
    db.refresh(itinerary)
    return _serialize_itinerary(db, itinerary)


def move_to_review(db: Session, group_id: int, user_id: int):
    _require_active_membership(db, group_id, user_id)
    itinerary = _latest_itinerary(db, group_id)
    if not itinerary:
        raise ValueError("ITINERARY_NOT_FOUND")
    if itinerary.state != "DRAFT":
        raise ValueError("INVALID_STATE")
    itinerary.state = "REVIEW"
    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)
    return _serialize_itinerary(db, itinerary)


def cast_vote(db: Session, group_id: int, user_id: int, value: str):
    _require_active_membership(db, group_id, user_id)
    itinerary = _latest_itinerary(db, group_id)
    if not itinerary:
        raise ValueError("ITINERARY_NOT_FOUND")
    if itinerary.state != "REVIEW":
        raise ValueError("INVALID_STATE")

    existing = db.query(Vote).filter(Vote.itinerary_id == itinerary.id, Vote.user_id == user_id).first()
    if existing:
        raise ValueError("DUPLICATE_VOTE")

    vote = Vote(itinerary_id=itinerary.id, group_id=group_id, user_id=user_id, value=value)
    db.add(vote)
    db.commit()
    db.refresh(vote)
    return vote


def lock_itinerary(db: Session, group_id: int, user_id: int):
    membership = _require_active_membership(db, group_id, user_id)
    if membership.role != "HOST":
        raise ValueError("FORBIDDEN")

    itinerary = _latest_itinerary(db, group_id)
    if not itinerary:
        raise ValueError("ITINERARY_NOT_FOUND")
    if itinerary.state != "REVIEW":
        raise ValueError("INVALID_STATE")

    itinerary.state = "LOCKED"
    db.add(itinerary)

    group = db.query(Group).filter(Group.id == group_id).first()
    members = db.query(Membership).filter(Membership.group_id == group_id, Membership.status == "ACTIVE").all()
    for member in members:
        db.add(
            Notification(
                user_id=member.user_id,
                group_id=group_id,
                kind="ITINERARY_LOCKED",
                message=f'Itinerary locked for "{group.name}".',
            )
        )

    db.commit()
    db.refresh(itinerary)
    return _serialize_itinerary(db, itinerary)
