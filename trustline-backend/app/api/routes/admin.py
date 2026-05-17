from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.schemas.admin import AdminDashboardResponse
from app.schemas.complaint import (
    ComplaintAssignRequest,
    ComplaintInternalNoteRequest,
    ComplaintPriorityUpdateRequest,
    ComplaintResponse,
    ComplaintStatusUpdateRequest,
)
from app.services.admin_service import get_complaint_queue, get_dashboard_summary
from app.services.complaint_service import (
    add_internal_note,
    assign_reviewer,
    get_complaint_or_404,
    update_priority,
    update_status,
)

router = APIRouter()


@router.get("/dashboard", response_model=AdminDashboardResponse)
def dashboard(db: Session = Depends(get_db), _admin: User = Depends(get_current_admin)):
    return get_dashboard_summary(db)


@router.get("/complaints/queue", response_model=list[ComplaintResponse])
def queue(
    status: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return get_complaint_queue(db, status=status, priority=priority)


@router.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
def detail(complaint_id: int, db: Session = Depends(get_db), _admin: User = Depends(get_current_admin)):
    return get_complaint_or_404(db, complaint_id)


@router.patch("/complaints/{complaint_id}/assign", response_model=ComplaintResponse)
def assign(
    complaint_id: int,
    payload: ComplaintAssignRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    complaint = get_complaint_or_404(db, complaint_id)
    return assign_reviewer(db, complaint, payload.admin_user_id, current_admin.id)


@router.patch("/complaints/{complaint_id}/status", response_model=ComplaintResponse)
def change_status(
    complaint_id: int,
    payload: ComplaintStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    complaint = get_complaint_or_404(db, complaint_id)
    return update_status(db, complaint, payload.status.value, current_admin.id)


@router.patch("/complaints/{complaint_id}/priority", response_model=ComplaintResponse)
def change_priority(
    complaint_id: int,
    payload: ComplaintPriorityUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    complaint = get_complaint_or_404(db, complaint_id)
    return update_priority(db, complaint, payload.priority.value, current_admin.id)


@router.patch("/complaints/{complaint_id}/internal-note", response_model=ComplaintResponse)
def internal_note(
    complaint_id: int,
    payload: ComplaintInternalNoteRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    complaint = get_complaint_or_404(db, complaint_id)
    return add_internal_note(db, complaint, payload.note, current_admin.id)
