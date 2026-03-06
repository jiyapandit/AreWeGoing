from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class ItineraryItemResponse(BaseModel):
    id: int
    title: str
    summary: str
    estimated_cost: int
    duration_hours: float
    rationale: str


class ItineraryDayResponse(BaseModel):
    day_number: int
    items: list[ItineraryItemResponse]


class ItineraryResponse(BaseModel):
    id: int
    group_id: int
    state: Literal["DRAFT", "REVIEW", "LOCKED"]
    confidence_score: int
    created_by: int
    created_at: datetime
    vote_summary: dict[str, int]
    days: list[ItineraryDayResponse]


class VoteRequest(BaseModel):
    value: Literal["APPROVE", "CHANGES"]


class VoteResponse(BaseModel):
    id: int
    group_id: int
    itinerary_id: int
    user_id: int
    value: Literal["APPROVE", "CHANGES"]
