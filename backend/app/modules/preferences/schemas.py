from pydantic import BaseModel, Field
from typing import List, Optional

class PreferencesUpsertRequest(BaseModel):
    destination_type: Optional[str] = Field(default=None, max_length=50)
    budget_min: Optional[int] = Field(default=None, ge=0)
    budget_max: Optional[int] = Field(default=None, ge=0)
    days: Optional[int] = Field(default=None, ge=1, le=60)

    activities: List[str] = Field(default_factory=list)
    transport_mode: Optional[str] = Field(default=None, max_length=40)

    dietary_preferences: List[str] = Field(default_factory=list)
    travel_pace: Optional[str] = Field(default=None, max_length=30)

class PreferencesResponse(BaseModel):
    user_id: int
    group_id: int
    destination_type: Optional[str]
    budget_min: Optional[int]
    budget_max: Optional[int]
    days: Optional[int]
    activities: List[str]
    transport_mode: Optional[str]
    dietary_preferences: List[str]
    travel_pace: Optional[str]

    class Config:
        from_attributes = True

class MemberPreferenceStatus(BaseModel):
    user_id: int
    email: str
    has_preferences: bool

class PreferencesStatusResponse(BaseModel):
    group_id: int
    completion_percent: int
    members: List[MemberPreferenceStatus]