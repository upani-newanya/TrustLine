from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import ComplaintPriorityEnum, ComplaintSourceEnum, ComplaintStatusEnum, RoleEnum
from app.models.complaint import Complaint
from app.models.user import User
from app.schemas.complaint import ComplaintCreateRequest
from app.services.audit_service import log_action
from app.services.notification_service import create_notification
from app.utils.case_id_generator import generate_case_id


def create_manual_complaint(db: Session, payload: ComplaintCreateRequest, reporter: User) -> Complaint:
    complaint = Complaint(
        case_id=generate_case_id(),
        title=payload.title,
        category=payload.category,
        incident_description=payload.incident_description,
        source_platform=payload.source_platform,
        incident_date=payload.incident_date,
        victim_name=payload.victim_name,
        victim_phone=payload.victim_phone,
        victim_address=payload.victim_address,
        guardian_phone=payload.guardian_phone,
        reporter_id=reporter.id,
        source_type=ComplaintSourceEnum.MANUAL.value,
        status=ComplaintStatusEnum.PENDING.value,
        priority=ComplaintPriorityEnum.MEDIUM.value,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    log_action(
        db,
        action="complaint_created",
        actor_user_id=reporter.id,
        entity_type="complaint",
        entity_id=str(complaint.id),
        metadata={"case_id": complaint.case_id, "source": "manual"},
    )
    return complaint


def create_chatbot_complaint(db: Session, data: dict, reporter: User) -> Complaint:
    complaint = Complaint(
        case_id=generate_case_id(),
        title=data["title"],
        category=data["category"],
        incident_description=data["incident_description"],
        source_platform=data.get("source_platform"),
        victim_name=data.get("victim_name"),
        victim_phone=data.get("victim_phone"),
        victim_address=data.get("victim_address"),
        guardian_phone=data.get("guardian_phone"),
        collected_fields=data.get("collected_fields"),
        reporter_id=reporter.id,
        source_type=ComplaintSourceEnum.CHATBOT.value,
        status=ComplaintStatusEnum.PENDING.value,
        priority=ComplaintPriorityEnum.MEDIUM.value,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    log_action(
        db,
        action="complaint_created",
        actor_user_id=reporter.id,
        entity_type="complaint",
        entity_id=str(complaint.id),
        metadata={"case_id": complaint.case_id, "source": "chatbot"},
    )
    return complaint


def get_complaint_or_404(db: Session, complaint_id: int) -> Complaint:
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    return complaint


def list_user_complaints(db: Session, user: User) -> list[Complaint]:
    if user.role == RoleEnum.ADMIN.value:
        return db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    return db.query(Complaint).filter(Complaint.reporter_id == user.id).order_by(Complaint.created_at.desc()).all()


def update_status(db: Session, complaint: Complaint, status_value: str, admin_user_id: int) -> Complaint:
    complaint.status = status_value
    db.commit()
    db.refresh(complaint)

    create_notification(
        db,
        user_id=complaint.reporter_id,
        title="Complaint Status Updated",
        body=f"Your complaint {complaint.case_id} is now '{status_value}'.",
    )
    log_action(
        db,
        action="complaint_status_changed",
        actor_user_id=admin_user_id,
        entity_type="complaint",
        entity_id=str(complaint.id),
        metadata={"status": status_value},
    )
    return complaint


def update_priority(db: Session, complaint: Complaint, priority_value: str, admin_user_id: int) -> Complaint:
    complaint.priority = priority_value
    db.commit()
    db.refresh(complaint)
    log_action(
        db,
        action="complaint_priority_changed",
        actor_user_id=admin_user_id,
        entity_type="complaint",
        entity_id=str(complaint.id),
        metadata={"priority": priority_value},
    )
    return complaint


def assign_reviewer(db: Session, complaint: Complaint, admin_user_id: int, actor_user_id: int) -> Complaint:
    admin_user = db.query(User).filter(User.id == admin_user_id, User.role == RoleEnum.ADMIN.value).first()
    if not admin_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected user is not an admin")

    complaint.assigned_admin_id = admin_user_id
    db.commit()
    db.refresh(complaint)

    create_notification(
        db,
        user_id=admin_user_id,
        title="New Complaint Assigned",
        body=f"Complaint {complaint.case_id} has been assigned to you.",
    )
    log_action(
        db,
        action="admin_assigned",
        actor_user_id=actor_user_id,
        entity_type="complaint",
        entity_id=str(complaint.id),
        metadata={"assigned_admin_id": admin_user_id},
    )
    return complaint


def add_internal_note(db: Session, complaint: Complaint, note: str, admin_user_id: int) -> Complaint:
    complaint.internal_notes = note
    db.commit()
    db.refresh(complaint)
    log_action(
        db,
        action="complaint_internal_note_added",
        actor_user_id=admin_user_id,
        entity_type="complaint",
        entity_id=str(complaint.id),
    )
    return complaint
