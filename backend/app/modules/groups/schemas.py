from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    is_public: bool = False

class GroupResponse(BaseModel):
    id: int
    name: str
    is_public: bool
    join_code: str
    created_by: int
    created_at: datetime

class JoinGroupRequest(BaseModel):
    join_code: str = Field(min_length=4, max_length=20)


class GroupMemberResponse(BaseModel):
    id: int
    email: str
    role: str
    status: Literal["PENDING", "ACTIVE", "REJECTED"]


class GroupMembersListResponse(BaseModel):
    group_id: int
    members: list[GroupMemberResponse]


class JoinRequestResponse(BaseModel):
    group_id: int
    membership_id: int
    status: Literal["PENDING", "ACTIVE", "REJECTED"]


class UpdateMembershipStatusRequest(BaseModel):
    status: Literal["ACTIVE", "REJECTED"]


class GroupMetricsResponse(BaseModel):
    group_id: int
    groupSize: int
    preferenceCompletionPercent: int
    budgetAlignmentScore: int
    activityMatchScore: int
    conflictCount: int
    itineraryConfidenceScore: int
    approvalStatus: str
