import secrets
import os
import smtplib
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from sqlalchemy.orm import Session

from db.models.group import Group
from db.models.group_metric_snapshot import GroupMetricSnapshot
from db.models.invite import Invite
from db.models.invite_delivery_attempt import InviteDeliveryAttempt
from db.models.membership import Membership
from db.models.notification import Notification
from db.models.preference import Preference
from db.models.itinerary import Itinerary
from db.models.vote import Vote
from db.models.user import User


def _send_invite_email_once(group: Group, recipient_email: str, invite_id: int, attempt_number: int):
    provider = os.getenv("INVITE_EMAIL_PROVIDER", "smtp").strip().lower()
    app_base_url = os.getenv("APP_BASE_URL", "http://localhost:5173")

    if provider == "noop":
        message_id = f"noop-{invite_id}-{attempt_number}"
        return True, "noop", message_id, None

    if provider != "smtp":
        return False, provider, None, f"UNSUPPORTED_PROVIDER:{provider}"

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM")

    if not smtp_host or not smtp_from:
        return False, "smtp", None, "SMTP_NOT_CONFIGURED"

    invite_link = f"{app_base_url.rstrip('/')}/join-group?code={group.join_code}"
    message = EmailMessage()
    message["Subject"] = f'Invite to join "{group.name}"'
    message["From"] = smtp_from
    message["To"] = recipient_email
    message.set_content(
        f'You were invited to join "{group.name}".\n'
        f"Join code: {group.join_code}\n"
        f"Join link: {invite_link}\n"
    )

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(message)
        message_id = message.get("Message-Id") or f"smtp-{invite_id}-{attempt_number}"
        return True, "smtp", message_id, None
    except Exception as error:
        # Delivery failures are tracked and can be reconciled via webhook/retry.
        return False, "smtp", None, str(error)


def _record_delivery_attempt(
    db: Session,
    invite: Invite,
    attempt_number: int,
    provider: str,
    status: str,
    provider_message_id: str | None = None,
    error_message: str | None = None,
):
    db.add(
        InviteDeliveryAttempt(
            invite_id=invite.id,
            attempt_number=attempt_number,
            provider=provider,
            status=status,
            provider_message_id=provider_message_id,
            error_message=error_message,
        )
    )


def _deliver_invite_email_with_retries(db: Session, invite: Invite, group: Group):
    max_retries = max(1, int(os.getenv("INVITE_EMAIL_MAX_RETRIES", "3")))
    retry_delay_seconds = max(0.0, float(os.getenv("INVITE_EMAIL_RETRY_DELAY_SECONDS", "0")))

    last_error = None
    for attempt in range(1, max_retries + 1):
        ok, provider, provider_message_id, error_message = _send_invite_email_once(group, invite.email, invite.id, attempt)
        invite.delivery_provider = provider
        invite.delivery_attempts = attempt
        invite.delivery_last_attempt_at = datetime.now(timezone.utc)
        if ok:
            invite.delivery_status = "DELIVERED"
            invite.delivery_provider_id = provider_message_id
            invite.delivery_last_error = None
            _record_delivery_attempt(
                db=db,
                invite=invite,
                attempt_number=attempt,
                provider=provider or "unknown",
                status="DELIVERED",
                provider_message_id=provider_message_id,
                error_message=None,
            )
            db.add(invite)
            db.commit()
            db.refresh(invite)
            return

        last_error = error_message or "UNKNOWN_DELIVERY_ERROR"
        invite.delivery_last_error = last_error
        _record_delivery_attempt(
            db=db,
            invite=invite,
            attempt_number=attempt,
            provider=provider or "unknown",
            status="FAILED",
            provider_message_id=provider_message_id,
            error_message=last_error,
        )
        if last_error == "SMTP_NOT_CONFIGURED":
            invite.delivery_status = "PENDING"
            db.add(invite)
            db.commit()
            db.refresh(invite)
            return

        if attempt < max_retries and retry_delay_seconds > 0:
            db.add(invite)
            db.commit()
            time.sleep(retry_delay_seconds)

    invite.delivery_status = "FAILED"
    db.add(invite)
    db.add(
        Notification(
            user_id=invite.inviter_user_id,
            group_id=invite.group_id,
            kind="INVITE_EMAIL_FAILED",
            message=f'Invite email to "{invite.email}" failed after {max_retries} attempts.',
        )
    )
    db.commit()
    db.refresh(invite)


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

    if membership.status == new_status:
        return membership

    group = db.query(Group).filter(Group.id == group_id).first()
    membership.status = new_status
    db.add(membership)
    if membership.role == "MEMBER":
        if new_status == "ACTIVE":
            db.add(
                Notification(
                    user_id=membership.user_id,
                    group_id=group_id,
                    kind="JOIN_REQUEST_APPROVED",
                    message=f'Your request to join "{group.name if group else f"Group #{group_id}"}" was approved.',
                )
            )
        elif new_status == "REJECTED":
            db.add(
                Notification(
                    user_id=membership.user_id,
                    group_id=group_id,
                    kind="JOIN_REQUEST_REJECTED",
                    message=f'Your request to join "{group.name if group else f"Group #{group_id}"}" was rejected.',
                )
            )
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
            "budgetConflict": False,
            "transportConflict": False,
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
        "budgetConflict": budget_conflicts > 0,
        "transportConflict": transport_conflicts > 0,
        "itineraryConfidenceScore": itinerary_confidence,
        "approvalStatus": approval_status,
    }


def create_group_metric_snapshot(db: Session, group_id: int, user_id: int):
    metrics = get_group_metrics(db, group_id, user_id)
    snapshot = GroupMetricSnapshot(
        group_id=group_id,
        captured_by=user_id,
        group_size=metrics["groupSize"],
        preference_completion_percent=metrics["preferenceCompletionPercent"],
        budget_alignment_score=metrics["budgetAlignmentScore"],
        activity_match_score=metrics["activityMatchScore"],
        conflict_count=metrics["conflictCount"],
        itinerary_confidence_score=metrics["itineraryConfidenceScore"],
        approval_status=metrics["approvalStatus"],
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return {
        "id": snapshot.id,
        "group_id": snapshot.group_id,
        "groupSize": snapshot.group_size,
        "preferenceCompletionPercent": snapshot.preference_completion_percent,
        "budgetAlignmentScore": snapshot.budget_alignment_score,
        "activityMatchScore": snapshot.activity_match_score,
        "conflictCount": snapshot.conflict_count,
        "itineraryConfidenceScore": snapshot.itinerary_confidence_score,
        "approvalStatus": snapshot.approval_status,
        "created_at": snapshot.created_at,
    }


def list_group_metric_snapshots(db: Session, group_id: int, user_id: int, limit: int = 15):
    _ = get_group_metrics(db, group_id, user_id)
    rows = (
        db.query(GroupMetricSnapshot)
        .filter(GroupMetricSnapshot.group_id == group_id)
        .order_by(GroupMetricSnapshot.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": row.id,
            "group_id": row.group_id,
            "groupSize": row.group_size,
            "preferenceCompletionPercent": row.preference_completion_percent,
            "budgetAlignmentScore": row.budget_alignment_score,
            "activityMatchScore": row.activity_match_score,
            "conflictCount": row.conflict_count,
            "itineraryConfidenceScore": row.itinerary_confidence_score,
            "approvalStatus": row.approval_status,
            "created_at": row.created_at,
        }
        for row in rows
    ]


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

    invite = Invite(
        group_id=group_id,
        inviter_user_id=inviter_user_id,
        email=email.strip().lower(),
        status="SENT",
        delivery_status="PENDING",
    )
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
    _deliver_invite_email_with_retries(db, invite, group)
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
            "delivery_status": invite.delivery_status,
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


def process_invite_delivery_webhook(
    db: Session,
    invite_id: int,
    delivery_status: str,
    provider: str | None = None,
    provider_message_id: str | None = None,
    error_message: str | None = None,
) -> Invite:
    invite = db.query(Invite).filter(Invite.id == invite_id).first()
    if not invite:
        raise ValueError("INVITE_NOT_FOUND")

    valid_statuses = {"DELIVERED", "FAILED", "BOUNCED"}
    normalized = delivery_status.strip().upper()
    if normalized not in valid_statuses:
        raise ValueError("INVALID_DELIVERY_STATUS")

    next_attempt = (invite.delivery_attempts or 0) + 1
    _record_delivery_attempt(
        db=db,
        invite=invite,
        attempt_number=next_attempt,
        provider=(provider or invite.delivery_provider or "webhook").lower(),
        status=normalized,
        provider_message_id=provider_message_id,
        error_message=error_message,
    )

    invite.delivery_attempts = next_attempt
    invite.delivery_status = normalized
    invite.delivery_provider = (provider or invite.delivery_provider or "webhook").lower()
    invite.delivery_provider_id = provider_message_id or invite.delivery_provider_id
    invite.delivery_last_error = error_message if normalized != "DELIVERED" else None
    invite.delivery_last_attempt_at = datetime.now(timezone.utc)
    db.add(invite)

    if normalized in {"FAILED", "BOUNCED"}:
        db.add(
            Notification(
                user_id=invite.inviter_user_id,
                group_id=invite.group_id,
                kind="INVITE_EMAIL_FAILED",
                message=f'Invite email to "{invite.email}" reported {normalized.lower()}.',
            )
        )

    db.commit()
    db.refresh(invite)
    return invite
