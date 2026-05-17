from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(db: Session, user_id: int, title: str, body: str) -> Notification:
    notification = Notification(user_id=user_id, title=title, body=body)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(db: Session, user_id: int) -> list[Notification]:
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()


def mark_as_read(db: Session, user_id: int, notification_id: int) -> Notification:
    notification = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.id == notification_id)
        .first()
    )
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
