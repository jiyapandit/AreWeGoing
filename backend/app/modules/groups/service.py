import secrets
from sqlalchemy.orm import Session

from db.models.group import Group
from db.models.invite import Invite
from db.models.membership import Membership
from db.models.notification import Notification
from db.models.preference import Preference
from db.models.itinerary import Itinerary
from db.models.vote import Vote
from db.models.user import User


def _generate_join_code() -> str:
    # short, shareable, URL-safe; remove confusing chars by uppercasing and trimming
    return secrets.token_urlsafe(6).replace("-", "").replace("_", "").upper()[:10]

def create_group(db: Session, user_id: int, name: str, is_public: bool) -> Group:
    # generate join_code with collision retry
    for _ in range(10):
        code = _generate_join_code()
        exists = db.query(Group).filter(Group.join_code == code).first()
        if not exists:
            group = Group(name=name, is_public=is_public, join_code=code, created_by=user_id)
            db.add(group)
            db.commit()
            db.refresh(group)

            host_membership = Membership(user_id=user_id, group_id=group.id, role="HOST", status="ACTIVE")
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

    membership = Membership(user_id=user_id, group_id=group.id, role="MEMBER", status="ACTIVE")
    db.add(membership)
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        sent_invites = db.query(Invite).filter(
            Invite.group_id == group.id,
            Invite.email == user.email.strip().lower(),
            Invite.status == "SENT",
        ).all()
        notifier_ids = set()
        for invite in sent_invites:
            invite.status = "ACCEPTED"
            db.add(invite)
            notifier_ids.add(invite.inviter_user_id)
        for inviter_id in notifier_ids:
            db.add(
                Notification(
                    user_id=inviter_id,
                    group_id=group.id,
                    kind="INVITE_ACCEPTED",
                    message=f'{user.email} accepted your invite to "{group.name}".',
                )
            )
    db.commit()
    return group


def request_join_public_group(db: Session, user_id: int, group_id: int) -> Membership:
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("GROUP_NOT_FOUND")
    if not group.is_public:
        raise ValueError("GROUP_NOT_PUBLIC")

    existing = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.group_id == group.id
    ).first()
    if existing:
        raise ValueError("ALREADY_MEMBER")

    membership = Membership(user_id=user_id, group_id=group.id, role="MEMBER", status="PENDING")
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def update_membership_status(db: Session, group_id: int, actor_id: int, membership_id: int, new_status: str) -> Membership:
    host_membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == actor_id,
        Membership.role == "HOST",
        Membership.status == "ACTIVE"
    ).first()
    if not host_membership:
        raise ValueError("FORBIDDEN")

    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.group_id == group_id
    ).first()
    if not membership:
        raise ValueError("MEMBERSHIP_NOT_FOUND")

    membership.status = new_status
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership

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
                "role": m.role,
                "status": m.status
            })

    return results

def get_group_details(db: Session, user_id: int, group_id: int):
    # Ensure user belongs to group
    membership = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.group_id == group_id
    ).first()

    if not membership or membership.status != "ACTIVE":
        raise ValueError("FORBIDDEN")

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("GROUP_NOT_FOUND")

    members = db.query(Membership).filter(
        Membership.group_id == group_id
    ).all()

    member_list = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            member_list.append({
                "id": user.id,
                "email": user.email,
                "role": m.role,
                "status": m.status
            })

    return {
        "id": group.id,
        "name": group.name,
        "is_public": group.is_public,
        "join_code": group.join_code,
        "created_by": group.created_by,
        "created_at": group.created_at,
        "members": member_list
    }


def list_public_groups(db: Session, limit: int = 30):
    groups = (
        db.query(Group)
        .filter(Group.is_public.is_(True))
        .order_by(Group.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": group.id,
            "name": group.name,
            "is_public": group.is_public,
            "join_code": group.join_code,
            "created_by": group.created_by,
            "created_at": group.created_at,
        }
        for group in groups
    ]


def get_group_members(db: Session, group_id: int, user_id: int):
    membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == user_id,
        Membership.status == "ACTIVE"
    ).first()
    if not membership:
        raise ValueError("FORBIDDEN")

    rows = db.query(Membership, User).join(User, User.id == Membership.user_id).filter(
        Membership.group_id == group_id
    ).all()
    return {
        "group_id": group_id,
        "members": [
            {
                "membership_id": member.id,
                "id": user.id,
                "email": user.email,
                "role": member.role,
                "status": member.status,
            }
            for member, user in rows
        ],
    }


def get_group_metrics(db: Session, group_id: int, user_id: int):
    membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == user_id,
        Membership.status == "ACTIVE"
    ).first()
    if not membership:
        raise ValueError("FORBIDDEN")

    active_members = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.status == "ACTIVE"
    ).all()
    active_user_ids = [m.user_id for m in active_members]
    group_size = len(active_user_ids)
    if group_size == 0:
        return {
            "group_id": group_id,
            "groupSize": 0,
            "preferenceCompletionPercent": 0,
            "budgetAlignmentScore": 0,
            "activityMatchScore": 0,
            "conflictCount": 0,
            "itineraryConfidenceScore": 0,
            "approvalStatus": "NOT_STARTED",
        }

    prefs = db.query(Preference).filter(
        Preference.group_id == group_id,
        Preference.user_id.in_(active_user_ids)
    ).all()
    pref_by_user = {pref.user_id: pref for pref in prefs}
    completion_percent = int((len(pref_by_user) / group_size) * 100)

    mins = [p.budget_min for p in prefs if p.budget_min is not None]
    maxs = [p.budget_max for p in prefs if p.budget_max is not None]
    budget_alignment_score = 0
    budget_conflicts = 0
    if mins and maxs:
        overlap_start = max(mins)
        overlap_end = min(maxs)
        if overlap_start <= overlap_end:
            span = max(max(maxs) - min(mins), 1)
            overlap = overlap_end - overlap_start
            budget_alignment_score = int(max(0, min(100, (overlap / span) * 100)))
        else:
            budget_conflicts = 1
            budget_alignment_score = 0

    activity_sets = [set(p.activities or []) for p in prefs if p.activities]
    activity_match_score = 0
    if activity_sets:
        inter = set.intersection(*activity_sets) if len(activity_sets) > 1 else activity_sets[0]
        union = set.union(*activity_sets)
        activity_match_score = int((len(inter) / max(len(union), 1)) * 100)

    transport_modes = {p.transport_mode for p in prefs if p.transport_mode}
    transport_conflicts = 1 if len(transport_modes) > 1 else 0
    conflict_count = budget_conflicts + transport_conflicts

    itinerary_confidence = int(
        max(0, min(100, (completion_percent * 0.35) + (budget_alignment_score * 0.35) + (activity_match_score * 0.30) - (conflict_count * 10)))
    )

    itinerary = db.query(Itinerary).filter(Itinerary.group_id == group_id).order_by(Itinerary.id.desc()).first()
    approval_status = "NOT_STARTED"
    if itinerary:
        approval_status = itinerary.state
        if itinerary.state == "REVIEW":
            total_votes = db.query(Vote).filter(Vote.itinerary_id == itinerary.id).count()
            approve_votes = db.query(Vote).filter(Vote.itinerary_id == itinerary.id, Vote.value == "APPROVE").count()
            if total_votes > 0:
                approval_status = f"REVIEW {approve_votes}/{total_votes} APPROVE"

    return {
        "group_id": group_id,
        "groupSize": group_size,
        "preferenceCompletionPercent": completion_percent,
        "budgetAlignmentScore": budget_alignment_score,
        "activityMatchScore": activity_match_score,
        "conflictCount": conflict_count,
        "itineraryConfidenceScore": itinerary_confidence,
        "approvalStatus": approval_status,
    }


def send_group_invite(db: Session, group_id: int, inviter_user_id: int, email: str):
    membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == inviter_user_id,
        Membership.status == "ACTIVE",
        Membership.role == "HOST",
    ).first()
    if not membership:
        raise ValueError("FORBIDDEN")

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("GROUP_NOT_FOUND")

    invite = Invite(group_id=group_id, inviter_user_id=inviter_user_id, email=email.strip().lower(), status="SENT")
    db.add(invite)

    invited_user = db.query(User).filter(User.email == email.strip().lower()).first()
    if invited_user:
        db.add(
            Notification(
                user_id=invited_user.id,
                group_id=group_id,
                kind="GROUP_INVITE",
                message=f'You were invited to join "{group.name}" ({group.join_code}).',
            )
        )

    db.commit()
    db.refresh(invite)
    return invite


def list_group_invites(db: Session, group_id: int, user_id: int):
    membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == user_id,
        Membership.status == "ACTIVE",
    ).first()
    if not membership:
        raise ValueError("FORBIDDEN")

    rows = db.query(Invite).filter(Invite.group_id == group_id).order_by(Invite.created_at.desc()).all()
    return rows


def list_user_invites(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    rows = (
        db.query(Invite, Group)
        .join(Group, Group.id == Invite.group_id)
        .filter(Invite.email == user.email.strip().lower(), Invite.status == "SENT")
        .order_by(Invite.created_at.desc())
        .all()
    )

    return [
        {
            "id": invite.id,
            "group_id": invite.group_id,
            "group_name": group.name,
            "join_code": group.join_code,
            "inviter_user_id": invite.inviter_user_id,
            "email": invite.email,
            "status": invite.status,
            "created_at": invite.created_at,
        }
        for invite, group in rows
    ]


def update_group_invite_status(db: Session, group_id: int, invite_id: int, actor_id: int, new_status: str) -> Invite:
    host_membership = db.query(Membership).filter(
        Membership.group_id == group_id,
        Membership.user_id == actor_id,
        Membership.status == "ACTIVE",
        Membership.role == "HOST",
    ).first()
    if not host_membership:
        raise ValueError("FORBIDDEN")

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("GROUP_NOT_FOUND")

    invite = db.query(Invite).filter(Invite.id == invite_id, Invite.group_id == group_id).first()
    if not invite:
        raise ValueError("INVITE_NOT_FOUND")

    if new_status == "REVOKED":
        if invite.status == "REVOKED":
            return invite
        if invite.status != "SENT":
            raise ValueError("INVITE_NOT_REVOCABLE")
        invite.status = "REVOKED"
        db.add(invite)
        db.commit()
        db.refresh(invite)
        return invite

    raise ValueError("INVALID_STATUS")


def accept_group_invite(db: Session, invite_id: int, user_id: int) -> Invite:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("FORBIDDEN")

    invite = db.query(Invite).filter(Invite.id == invite_id).first()
    if not invite:
        raise ValueError("INVITE_NOT_FOUND")

    if invite.email.strip().lower() != user.email.strip().lower():
        raise ValueError("FORBIDDEN")

    group = db.query(Group).filter(Group.id == invite.group_id).first()
    if not group:
        raise ValueError("GROUP_NOT_FOUND")

    if invite.status == "REVOKED":
        raise ValueError("INVITE_NOT_ACTIVE")

    membership = db.query(Membership).filter(
        Membership.group_id == invite.group_id,
        Membership.user_id == user_id,
    ).first()
    if membership:
        if membership.status != "ACTIVE":
            membership.status = "ACTIVE"
            membership.role = "MEMBER"
            db.add(membership)
    else:
        db.add(Membership(user_id=user_id, group_id=invite.group_id, role="MEMBER", status="ACTIVE"))

    if invite.status != "ACCEPTED":
        invite.status = "ACCEPTED"
        db.add(invite)
        db.add(
            Notification(
                user_id=invite.inviter_user_id,
                group_id=invite.group_id,
                kind="INVITE_ACCEPTED",
                message=f'{user.email} accepted your invite to "{group.name}".',
            )
        )

    db.commit()
    db.refresh(invite)
    return invite
