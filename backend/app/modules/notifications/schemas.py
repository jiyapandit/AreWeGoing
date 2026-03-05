from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    group_id: int | None
    kind: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationReadResponse(BaseModel):
    id: int
    is_read: bool
