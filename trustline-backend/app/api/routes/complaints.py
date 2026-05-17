from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import RoleEnum
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.complaint import ComplaintCreateRequest, ComplaintResponse
from app.services.complaint_service import create_manual_complaint, get_complaint_or_404, list_user_complaints

router = APIRouter()


@router.post("", response_model=ComplaintResponse)
def create_complaint(
    payload: ComplaintCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [RoleEnum.USER.value, RoleEnum.GUARDIAN.value]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only users can create complaints")
    return create_manual_complaint(db, payload, current_user)


@router.get("", response_model=list[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_user_complaints(db, current_user)


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def complaint_detail(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    complaint = get_complaint_or_404(db, complaint_id)
    if current_user.role != RoleEnum.ADMIN.value and complaint.reporter_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return complaint
