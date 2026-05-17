from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import ComplaintStatusEnum
from app.models.complaint import Complaint


def get_dashboard_summary(db: Session) -> dict:
    total = db.query(func.count(Complaint.id)).scalar() or 0

    def count_by_status(status: ComplaintStatusEnum) -> int:
        return db.query(func.count(Complaint.id)).filter(Complaint.status == status.value).scalar() or 0

    return {
        "total_complaints": total,
        "pending_count": count_by_status(ComplaintStatusEnum.PENDING),
        "under_review_count": count_by_status(ComplaintStatusEnum.UNDER_REVIEW),
        "need_more_info_count": count_by_status(ComplaintStatusEnum.NEED_MORE_INFO),
        "escalated_count": count_by_status(ComplaintStatusEnum.ESCALATED),
        "closed_count": count_by_status(ComplaintStatusEnum.CLOSED),
    }


def get_complaint_queue(db: Session, status: str | None = None, priority: str | None = None) -> list[Complaint]:
    query = db.query(Complaint)
    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)
    return query.order_by(Complaint.created_at.desc()).all()
