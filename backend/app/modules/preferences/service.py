from sqlalchemy.orm import Session
from db.models import Preference, Membership, User

def upsert_preferences(db: Session, group_id: int, user_id: int, payload):
    # Ensure user is a member of this group
    membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == user_id
    ).first()
    if not membership:
        return None  # router will convert to 403

    pref = db.query(Preference).filter(
        Preference.group_id == group_id,
        Preference.user_id == user_id
    ).first()

    if not pref:
        pref = Preference(group_id=group_id, user_id=user_id)

    pref.destination_type = payload.destination_type
    pref.budget_min = payload.budget_min
    pref.budget_max = payload.budget_max
    pref.days = payload.days
    pref.activities = payload.activities
    pref.transport_mode = payload.transport_mode
    pref.dietary_preferences = payload.dietary_preferences
    pref.travel_pace = payload.travel_pace

    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref

def get_my_preferences(db: Session, group_id: int, user_id: int):
    membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == user_id
    ).first()
    if not membership:
        return None

    return db.query(Preference).filter(
        Preference.group_id == group_id,
        Preference.user_id == user_id
    ).first()

def get_preferences_status(db: Session, group_id: int):
    members = db.query(Membership, User).join(User, User.id == Membership.user_id).filter(
        Membership.group_id == group_id
    ).all()

    member_rows = []
    filled = 0

    for membership, user in members:
        has_pref = db.query(Preference).filter(
            Preference.group_id == group_id,
            Preference.user_id == user.id
        ).first() is not None

        if has_pref:
            filled += 1

        member_rows.append({
            "user_id": user.id,
            "email": user.email,
            "has_preferences": has_pref
        })

    total = len(member_rows)
    completion = int((filled / total) * 100) if total > 0 else 0

    return {
        "group_id": group_id,
        "completion_percent": completion,
        "members": member_rows
    }