from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.chatbot import ChatSession, ChatSessionMessage
from app.models.user import User
from app.schemas.chatbot import ChatFinalizeRequest
from app.services.complaint_service import create_chatbot_complaint


def start_session(db: Session, user: User) -> ChatSession:
    session = ChatSession(session_id=uuid4().hex, user_id=user.id, draft_data={})
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def start_guest_session(db: Session) -> ChatSession:
    session = ChatSession(session_id=uuid4().hex, user_id=None, draft_data={})
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_or_404(db: Session, session_id: str, user_id: int) -> ChatSession:
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id, ChatSession.user_id == user_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    return session


def get_guest_session_or_404(db: Session, session_id: str) -> ChatSession:
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id, ChatSession.user_id.is_(None)).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")
    return session


def save_message(db: Session, session: ChatSession, sender: str, content: str) -> ChatSessionMessage:
    msg = ChatSessionMessage(chat_session_id=session.id, sender=sender, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def update_draft(db: Session, session: ChatSession, draft_data: dict) -> ChatSession:
    merged = session.draft_data.copy() if session.draft_data else {}
    merged.update(draft_data)
    session.draft_data = merged
    db.commit()
    db.refresh(session)
    return session


def submit_final(db: Session, session: ChatSession, payload: ChatFinalizeRequest, user: User):
    data = {
        "title": payload.title,
        "category": payload.category,
        "incident_description": payload.incident_description,
        "source_platform": payload.source_platform,
    }
    complaint = create_chatbot_complaint(db, data, user)
    session.is_submitted = True
    session.draft_data = data
    db.commit()
    return complaint
