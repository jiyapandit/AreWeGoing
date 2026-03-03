from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.core.auth import get_current_user
from db.models.user import User

from app.modules.groups.schemas import CreateGroupRequest, GroupResponse, JoinGroupRequest
from app.modules.groups.service import create_group, join_group
from app.modules.groups.service import get_user_groups
from app.modules.groups.service import get_group_details

router = APIRouter()

@router.post("", response_model=GroupResponse, status_code=201)
def create(payload: CreateGroupRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = create_group(db, current_user.id, payload.name, payload.is_public)
    return GroupResponse(id=group.id, name=group.name, is_public=group.is_public, join_code=group.join_code)

@router.post("/join", response_model=GroupResponse)
def join(payload: JoinGroupRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        group = join_group(db, current_user.id, payload.join_code)
        return GroupResponse(id=group.id, name=group.name, is_public=group.is_public, join_code=group.join_code)
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