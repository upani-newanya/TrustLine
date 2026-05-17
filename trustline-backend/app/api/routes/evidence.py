from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.evidence import EvidenceResponse
from app.services.evidence_service import list_evidence, upload_evidence

router = APIRouter()


@router.post("/{complaint_id}", response_model=EvidenceResponse)
def upload(
    complaint_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return upload_evidence(db, complaint_id, current_user, file)


@router.get("/{complaint_id}", response_model=list[EvidenceResponse])
def get_all(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_evidence(db, complaint_id, current_user)
