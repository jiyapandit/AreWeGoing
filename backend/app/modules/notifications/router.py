from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.deps import get_db
from app.modules.notifications.schemas import NotificationReadResponse, NotificationResponse
from app.modules.notifications.service import list_notifications, mark_notification_read
from db.models.user import User

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [
        NotificationResponse(
            id=row.id,
            group_id=row.group_id,
            kind=row.kind,
            message=row.message,
            is_read=row.is_read,
            created_at=row.created_at,
        )
        for row in list_notifications(db, current_user.id)
    ]


@router.patch("/{notification_id}/read", response_model=NotificationReadResponse)
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        row = mark_notification_read(db, current_user.id, notification_id)
        return NotificationReadResponse(id=row.id, is_read=row.is_read)
    except ValueError:
        raise HTTPException(status_code=404, detail="Notification not found")
