from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.constants import RoleEnum
from app.models.complaint import Complaint
from app.models.evidence import Evidence
from app.models.user import User
from app.services.audit_service import log_action
from app.utils.file_handler import save_upload_file
from app.utils.validators import validate_upload


settings = get_settings()


def upload_evidence(db: Session, complaint_id: int, user: User, upload_file: UploadFile) -> Evidence:
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    if user.role != RoleEnum.ADMIN.value and complaint.reporter_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to upload to this complaint")

    file_bytes = upload_file.file.read()
    file_size = len(file_bytes)
    file_type = validate_upload(upload_file, file_size, settings.max_upload_size_mb * 1024 * 1024)
    upload_file.file.seek(0)
    stored_file_name, file_path, _, original_name = save_upload_file(upload_file, settings.upload_dir)

    evidence = Evidence(
        complaint_id=complaint.id,
        uploaded_by=user.id,
        original_file_name=original_name,
        stored_file_name=stored_file_name,
        file_path=file_path,
        file_type=file_type,
        mime_type=upload_file.content_type or "application/octet-stream",
        file_size=file_size,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    log_action(
        db,
        action="evidence_uploaded",
        actor_user_id=user.id,
        entity_type="evidence",
        entity_id=str(evidence.id),
        metadata={"complaint_id": complaint.id},
    )
    return evidence


def list_evidence(db: Session, complaint_id: int, user: User) -> list[Evidence]:
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    if user.role != RoleEnum.ADMIN.value and complaint.reporter_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view this complaint")

    return db.query(Evidence).filter(Evidence.complaint_id == complaint_id).order_by(Evidence.created_at.desc()).all()
