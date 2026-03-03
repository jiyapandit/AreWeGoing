from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.core.auth import get_current_user
from db.models import User

from app.modules.preferences.schemas import (
    PreferencesUpsertRequest,
    PreferencesResponse,
    PreferencesStatusResponse
)
from app.modules.preferences.service import (
    upsert_preferences,
    get_my_preferences,
    get_preferences_status
)

router = APIRouter(prefix="/api/v1/groups", tags=["Preferences"])

@router.put("/{group_id}/preferences", response_model=PreferencesResponse)
def upsert_group_preferences(
    group_id: int,
    payload: PreferencesUpsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = upsert_preferences(db, group_id, current_user.id, payload)
    if pref is None:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    return pref

@router.get("/{group_id}/preferences/me", response_model=PreferencesResponse)
def my_group_preferences(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref = get_my_preferences(db, group_id, current_user.id)
    if pref is None:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return pref

@router.get("/{group_id}/preferences/status", response_model=PreferencesStatusResponse)
def group_preferences_status(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If user isn't a member, treat as forbidden (reuse get_my_preferences membership check)
    membership_check = get_my_preferences(db, group_id, current_user.id)
    if membership_check is None:
        raise HTTPException(status_code=403, detail="Not a member of this group")

    status = get_preferences_status(db, group_id)
    return status