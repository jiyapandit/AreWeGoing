from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.deps import get_db
from app.modules.itinerary.schemas import ItineraryResponse, VoteRequest, VoteResponse
from app.modules.itinerary.service import cast_vote, generate_itinerary, get_group_itinerary, lock_itinerary, move_to_review
from db.models.user import User

router = APIRouter(prefix="/api/v1/groups", tags=["Itinerary"])


@router.post("/{group_id}/itinerary/generate", response_model=ItineraryResponse)
def generate(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return ItineraryResponse(**generate_itinerary(db, group_id, current_user.id))
    except ValueError as e:
        code = str(e)
        if code == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Not a member of this group")
        if code == "GROUP_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Group not found")
        if code == "INVALID_STATE":
            raise HTTPException(status_code=409, detail="Generation is allowed only when itinerary is in DRAFT state")
        if code == "CATALOG_EMPTY":
            raise HTTPException(status_code=409, detail="Catalog is empty")
        raise


@router.get("/{group_id}/itinerary", response_model=ItineraryResponse)
def get_itinerary(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return ItineraryResponse(**get_group_itinerary(db, group_id, current_user.id))
    except ValueError as e:
        code = str(e)
        if code == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Not a member of this group")
        if code == "ITINERARY_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Itinerary not found")
        raise


@router.post("/{group_id}/itinerary/review", response_model=ItineraryResponse)
def to_review(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return ItineraryResponse(**move_to_review(db, group_id, current_user.id))
    except ValueError as e:
        code = str(e)
        if code == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Not a member of this group")
        if code == "ITINERARY_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Itinerary not found")
        if code == "INVALID_STATE":
            raise HTTPException(status_code=409, detail="Itinerary must be in DRAFT state")
        raise


@router.post("/{group_id}/vote", response_model=VoteResponse)
def vote(
    group_id: int,
    payload: VoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        row = cast_vote(db, group_id, current_user.id, payload.value)
        return VoteResponse(id=row.id, group_id=row.group_id, itinerary_id=row.itinerary_id, user_id=row.user_id, value=row.value)
    except ValueError as e:
        code = str(e)
        if code == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Not a member of this group")
        if code == "ITINERARY_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Itinerary not found")
        if code == "INVALID_STATE":
            raise HTTPException(status_code=409, detail="Voting is allowed in REVIEW state only")
        if code == "DUPLICATE_VOTE":
            raise HTTPException(status_code=409, detail="Vote already exists for this user")
        raise


@router.post("/{group_id}/itinerary/lock", response_model=ItineraryResponse)
def lock(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return ItineraryResponse(**lock_itinerary(db, group_id, current_user.id))
    except ValueError as e:
        code = str(e)
        if code == "FORBIDDEN":
            raise HTTPException(status_code=403, detail="Only host can lock itinerary")
        if code == "ITINERARY_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Itinerary not found")
        if code == "INVALID_STATE":
            raise HTTPException(status_code=409, detail="Itinerary must be in REVIEW state")
        if code == "LOCK_VOTES_INCOMPLETE":
            raise HTTPException(status_code=409, detail="All active members must vote before locking")
        if code == "LOCK_HAS_CHANGE_REQUESTS":
            raise HTTPException(status_code=409, detail="Cannot lock itinerary while change requests exist")
        if code == "LOCK_APPROVAL_THRESHOLD":
            raise HTTPException(status_code=409, detail="Approval threshold not met for lock")
        raise
