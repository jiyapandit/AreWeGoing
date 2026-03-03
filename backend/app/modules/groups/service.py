import secrets
from sqlalchemy.orm import Session

from db.models.group import Group
from db.models.membership import Membership

def _generate_join_code() -> str:
    # short, shareable, URL-safe; remove confusing chars by uppercasing and trimming
    return secrets.token_urlsafe(6).replace("-", "").replace("_", "").upper()[:10]

def create_group(db: Session, user_id: int, name: str, is_public: bool) -> Group:
    # generate join_code with collision retry
    for _ in range(10):
        code = _generate_join_code()
        exists = db.query(Group).filter(Group.join_code == code).first()
        if not exists:
            group = Group(name=name, is_public=is_public, join_code=code)
            db.add(group)
            db.commit()
            db.refresh(group)

            host_membership = Membership(user_id=user_id, group_id=group.id, role="HOST")
            db.add(host_membership)
            db.commit()
            return group

    raise RuntimeError("JOIN_CODE_GENERATION_FAILED")

def join_group(db: Session, user_id: int, join_code: str) -> Group:
    code = join_code.strip().upper()
    group = db.query(Group).filter(Group.join_code == code).first()
    if not group:
        raise ValueError("GROUP_NOT_FOUND")

    existing = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.group_id == group.id
    ).first()
    if existing:
        raise ValueError("ALREADY_MEMBER")

    membership = Membership(user_id=user_id, group_id=group.id, role="MEMBER")
    db.add(membership)
    db.commit()
    return group

def get_user_groups(db: Session, user_id: int):
    memberships = db.query(Membership).filter(
        Membership.user_id == user_id
    ).all()

    results = []
    for m in memberships:
        group = db.query(Group).filter(Group.id == m.group_id).first()
        if group:
            results.append({
                "id": group.id,
                "name": group.name,
                "is_public": group.is_public,
                "join_code": group.join_code,
                "role": m.role
            })

    return results