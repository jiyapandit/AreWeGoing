from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.core.auth import get_current_user
from db.models.user import User

from app.modules.groups.schemas import (
    CreateGroupRequest,
    GroupMembersListResponse,
    GroupMetricsResponse,
    GroupResponse,
    InviteRequest,
    InviteResponse,
    JoinGroupRequest,
    JoinRequestResponse,
    UpdateInviteStatusRequest,
    UserInviteResponse,
    UpdateMembershipStatusRequest,
)
from app.modules.groups.service import (
    accept_group_invite,
    create_group,
    get_group_details,
    get_group_members,
    get_group_metrics,
    get_user_groups,
    join_group,
    list_group_invites,
    list_user_invites,
    list_public_groups,
    request_join_public_group,
    send_group_invite,
    update_group_invite_status,
    update_membership_status,
)

router = APIRouter()

@router.post("", response_model=GroupResponse, status_code=201)
def create(payload: CreateGroupRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = create_group(db, current_user.id, payload.name, payload.is_public)
    return GroupResponse(
        id=group.id,
        name=group.name,
        is_public=group.is_public,
        join_code=group.join_code,
        created_by=group.created_by,
        created_at=group.created_at,
    )

@router.post("/join", response_model=GroupResponse)
def join(payload: JoinGroupRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        group = join_group(db, current_user.id, payload.join_code)
        return GroupResponse(
            id=group.id,
            name=group.name,
            is_public=group.is_public,
            join_code=group.join_code,
            created_by=group.created_by,
            created_at=group.created_at,
        )
    except ValueError as e:
        if str(e) == "GROUP_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Group not found")
        if str(e) == "ALREADY_MEMBER":
            raise HTTPException(status_code=409, detail="Already a member of this group")
        raise

@router.get("/my")
def my_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_groups(db, current_user.id)

@router.get("/public", response_model=list[GroupResponse])
def public_groups(db: Session = Depends(get_db)):
    groups = list_public_groups(db)
    return [GroupResponse(**group) for group in groups]


@router.post("/{group_id}/join-request", response_model=JoinRequestResponse, status_code=201)
def join_request(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        membership = request_join_public_group(db, current_user.id, group_id)
        return JoinRequestResponse(group_id=group_id, membership_id=membership.id, status=membership.status)
    except ValueError as e:
        if str(e) == "GROUP_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Group not found")
        if str(e) == "GROUP_NOT_PUBLIC":
            raise HTTPException(status_code=400, detail="Group is not public")
        if str(e) == "ALREADY_MEMBER":
            raise HTTPException(status_code=409, detail="Already requested or member")
        raise


@router.patch("/{group_id}/members/{membership_id}/status", response_model=JoinRequestResponse)
def set_member_status(
    group_id: int,
    membership_id: int,
    payload: UpdateMembershipStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        membership = update_membership_status(db, group_id, current_user.id, membership_id, payload.status)
        return JoinRequestResponse(group_id=group_id, membership_id=membership.id, status=membership.status)
    except ValueError as e:
        if str(e) == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Only host can update membership status")
        if str(e) == "MEMBERSHIP_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Membership not found")
        raise


@router.get("/{group_id}/members", response_model=GroupMembersListResponse)
def members(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        data = get_group_members(db, group_id, current_user.id)
        return GroupMembersListResponse(**data)
    except ValueError as e:
        if str(e) == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Not a member of this group")
        raise


@router.get("/{group_id}/metrics", response_model=GroupMetricsResponse)
def metrics(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return GroupMetricsResponse(**get_group_metrics(db, group_id, current_user.id))
    except ValueError as e:
        if str(e) == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Not a member of this group")
        raise


@router.post("/{group_id}/invites", response_model=InviteResponse, status_code=201)
def create_invite(
    group_id: int,
    payload: InviteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        invite = send_group_invite(db, group_id, current_user.id, payload.email)
        return InviteResponse(
            id=invite.id,
            group_id=invite.group_id,
            email=invite.email,
            status=invite.status,
            created_at=invite.created_at,
        )
    except ValueError as e:
        if str(e) == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Only host can send invites")
        if str(e) == "GROUP_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Group not found")
        raise


@router.get("/{group_id}/invites", response_model=list[InviteResponse])
def get_invites(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        rows = list_group_invites(db, group_id, current_user.id)
        return [
            InviteResponse(id=row.id, group_id=row.group_id, email=row.email, status=row.status, created_at=row.created_at)
            for row in rows
        ]
    except ValueError as e:
        if str(e) == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Not a member of this group")
        raise


@router.get("/invites/me", response_model=list[UserInviteResponse])
def get_my_invites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = list_user_invites(db, current_user.id)
    return [UserInviteResponse(**row) for row in rows]


@router.post("/invites/{invite_id}/accept", response_model=InviteResponse)
def accept_invite(invite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        invite = accept_group_invite(db, invite_id, current_user.id)
        return InviteResponse(
            id=invite.id,
            group_id=invite.group_id,
            email=invite.email,
            status=invite.status,
            created_at=invite.created_at,
        )
    except ValueError as e:
        if str(e) == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Invite does not belong to current user")
        if str(e) == "INVITE_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Invite not found")
        if str(e) == "GROUP_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Group not found")
        if str(e) == "INVITE_NOT_ACTIVE":
            raise HTTPException(status_code=409, detail="Invite is no longer active")
        raise


@router.patch("/{group_id}/invites/{invite_id}", response_model=InviteResponse)
def set_invite_status(
    group_id: int,
    invite_id: int,
    payload: UpdateInviteStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        invite = update_group_invite_status(db, group_id, invite_id, current_user.id, payload.status)
        return InviteResponse(
            id=invite.id,
            group_id=invite.group_id,
            email=invite.email,
            status=invite.status,
            created_at=invite.created_at,
        )
    except ValueError as e:
        if str(e) == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Only host can update invite status")
        if str(e) == "GROUP_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Group not found")
        if str(e) == "INVITE_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Invite not found")
        if str(e) == "INVITE_NOT_REVOCABLE":
            raise HTTPException(status_code=409, detail="Invite cannot be revoked in its current state")
        raise

@router.get("/{group_id}")
def group_details(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return get_group_details(db, current_user.id, group_id)
    except ValueError as e:
        if str(e) == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Not a member of this group")
        if str(e) == "GROUP_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Group not found")
        raise
