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
    JoinGroupRequest,
    JoinRequestResponse,
    UpdateMembershipStatusRequest,
)
from app.modules.groups.service import (
    create_group,
    get_group_details,
    get_group_members,
    get_group_metrics,
    get_user_groups,
    join_group,
    list_public_groups,
    request_join_public_group,
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
