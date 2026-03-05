from sqlalchemy.orm import Session

from db.models.notification import Notification


def create_notification(db: Session, user_id: int, group_id: int | None, kind: str, message: str):
    notification = Notification(user_id=user_id, group_id=group_id, kind=kind, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(db: Session, user_id: int):
    rows = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
    return rows


def mark_notification_read(db: Session, user_id: int, notification_id: int):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    if not notification:
        raise ValueError("NOT_FOUND")
    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
