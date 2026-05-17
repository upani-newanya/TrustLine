from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import RoleEnum
from app.models.complaint import Complaint
from app.models.message import ComplaintMessage
from app.models.user import User


def _check_access(complaint: Complaint, user: User) -> None:
    if user.role == RoleEnum.ADMIN.value:
        return
    if complaint.reporter_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for this complaint")


def send_message(db: Session, complaint_id: int, user: User, body: str) -> ComplaintMessage:
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    _check_access(complaint, user)

    msg = ComplaintMessage(
        complaint_id=complaint_id,
        sender_id=user.id,
        body=body,
        is_internal=False,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def list_messages(db: Session, complaint_id: int, user: User) -> list[ComplaintMessage]:
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    _check_access(complaint, user)

    return (
        db.query(ComplaintMessage)
        .filter(ComplaintMessage.complaint_id == complaint_id, ComplaintMessage.is_internal.is_(False))
        .order_by(ComplaintMessage.created_at.asc())
        .all()
    )
