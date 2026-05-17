from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.message import ComplaintMessageCreateRequest, ComplaintMessageResponse
from app.services.message_service import list_messages, send_message

router = APIRouter()


@router.post("/{complaint_id}", response_model=ComplaintMessageResponse)
def send(
    complaint_id: int,
    payload: ComplaintMessageCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return send_message(db, complaint_id, current_user, payload.body)


@router.get("/{complaint_id}", response_model=list[ComplaintMessageResponse])
def list_thread(complaint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_messages(db, complaint_id, current_user)
