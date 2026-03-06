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
    days_values = [p.days for p in prefs if p.days is not None]
    days = max(1, min(7, int(sum(days_values) / max(len(days_values), 1)) if days_values else 3))

    budget_min_values = [p.budget_min for p in prefs if p.budget_min is not None]
    budget_max_values = [p.budget_max for p in prefs if p.budget_max is not None]
    budget_floor = int(sum(budget_min_values) / max(len(budget_min_values), 1)) if budget_min_values else 30
    budget_cap = int(sum(budget_max_values) / max(len(budget_max_values), 1)) if budget_max_values else 120

    interests = set()
    destination_types = set()
    transport_modes = set()
    travel_paces = set()
    for p in prefs:
        interests.update((p.activities or []))
        if p.destination_type:
            destination_types.add(p.destination_type.strip().lower())
        if p.transport_mode:
            transport_modes.add(p.transport_mode.strip().lower())
        if p.travel_pace:
            travel_paces.add(p.travel_pace.strip().lower())

    candidates = db.query(CatalogItem).all()
    if not candidates:
        raise ValueError("CATALOG_EMPTY")

    scored = []
    for item in candidates:
        tags = {tag.strip() for tag in (item.tags_csv or "").split(",") if tag.strip()}
        normalized_tags = {tag.lower() for tag in tags}
        interest_overlap = interests.intersection(normalized_tags)
        interest_score = int((len(interest_overlap) / max(len(interests), 1)) * 40) if interests else 20

        if budget_floor <= item.estimated_budget <= budget_cap:
            budget_score = 25
        else:
            distance = min(abs(item.estimated_budget - budget_floor), abs(item.estimated_budget - budget_cap))
            budget_score = max(0, 25 - int(distance / 10))

        duration_target = 4.0 if "relaxed" in travel_paces else 2.5 if "fast" in travel_paces else 3.0
        duration_score = max(0, 15 - int(abs(float(item.duration_hours) - duration_target) * 5))

        destination_score = 10 if destination_types and destination_types.intersection(normalized_tags) else (5 if destination_types else 8)
        mobility_score = 10 if (not transport_modes or transport_modes.intersection(normalized_tags)) else 4

        score = interest_score + budget_score + duration_score + destination_score + mobility_score
        scored.append((score, item, interest_overlap, budget_score, duration_score, destination_score, mobility_score, tags))
    scored.sort(key=lambda x: x[0], reverse=True)

    selected = []
    used_primary_tags = set()
    for row in scored:
        item = row[1]
        raw_tags = [tag.strip().lower() for tag in (item.tags_csv or "").split(",") if tag.strip()]
        primary_tag = raw_tags[0] if raw_tags else item.title.lower()
        if primary_tag in used_primary_tags and len(selected) < max(days, 2):
            continue
        selected.append(row)
        used_primary_tags.add(primary_tag)
        if len(selected) >= max(days, 2):
            break
    if len(selected) < max(days, 2):
        for row in scored:
            if row not in selected:
                selected.append(row)
            if len(selected) >= max(days, 2):
                break

    confidence = int(sum([row[0] for row in selected[: min(len(selected), days)]]) / max(min(len(selected), days), 1))
    confidence = max(0, min(100, confidence))

    itinerary = Itinerary(group_id=group_id, state="DRAFT", confidence_score=confidence, created_by=user_id)
    db.add(itinerary)
    db.flush()

    for i in range(days):
        day = ItineraryDay(itinerary_id=itinerary.id, day_number=i + 1)
        db.add(day)
        db.flush()
        selected_row = selected[i % len(selected)]
        item = selected_row[1]
        overlap = sorted(list(selected_row[2]))[:3]
        budget_score = selected_row[3]
        duration_score = selected_row[4]
        destination_score = selected_row[5]
        mobility_score = selected_row[6]
        readable_overlap = ", ".join(overlap) if overlap else "general group interests"
        rationale = (
            f"Matched interests: {readable_overlap}; "
            f"budget fit score {budget_score}/25; pace-duration fit {duration_score}/15; "
            f"destination fit {destination_score}/10; mobility fit {mobility_score}/10."
        )
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

    active_members = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.status == "ACTIVE"
    ).all()
    active_member_count = len(active_members)
    total_votes = db.query(Vote).filter(Vote.itinerary_id == itinerary.id).count()
    approve_votes = db.query(Vote).filter(Vote.itinerary_id == itinerary.id, Vote.value == "APPROVE").count()
    change_votes = db.query(Vote).filter(Vote.itinerary_id == itinerary.id, Vote.value == "CHANGES").count()

    if total_votes < active_member_count:
        raise ValueError("LOCK_VOTES_INCOMPLETE")
    if change_votes > 0:
        raise ValueError("LOCK_HAS_CHANGE_REQUESTS")
    approval_ratio = approve_votes / max(total_votes, 1)
    if approval_ratio < 0.6:
        raise ValueError("LOCK_APPROVAL_THRESHOLD")

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
