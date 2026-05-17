import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_optional
from app.models.user import User
from app.schemas.chatbot import (
    ChatBotReplyResponse,
    ChatDraftUpdateRequest,
    ChatFinalizeRequest,
    ChatMessageCreateRequest,
    ChatMessageResponse,
    ChatSessionStartResponse,
)
from app.schemas.complaint import ComplaintResponse
from app.services.chatbot_service import get_session_or_404, get_guest_session_or_404, save_message, start_session, start_guest_session, submit_final, update_draft
from app.services.complaint_service import create_chatbot_complaint
from app.chatbot.session_manager import engine_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Session creation – works for authenticated users AND guests
# ---------------------------------------------------------------------------

@router.post("/sessions", response_model=ChatSessionStartResponse)
def start_chat_session(db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        session = start_session(db, current_user)
    else:
        session = start_guest_session(db)
    return ChatSessionStartResponse(session_id=session.session_id)


# ---------------------------------------------------------------------------
# Post message – works for authenticated users AND guests
# ---------------------------------------------------------------------------

@router.post("/sessions/{session_id}/messages", response_model=ChatBotReplyResponse)
def post_user_message(
    session_id: str,
    payload: ChatMessageCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if current_user:
        chat_session = get_session_or_404(db, session_id, current_user.id)
    else:
        chat_session = get_guest_session_or_404(db, session_id)

    # 1. Save user message to DB
    user_msg = save_message(db, chat_session, sender="user", content=payload.content)

    # 2. Run MithuruEngine to generate bot reply
    engine = engine_manager.get_or_create(session_id)
    try:
        bot_reply_text = engine.process_message(payload.content)
    except Exception as exc:
        logger.error("MithuruEngine error for session %s: %s", session_id, exc, exc_info=True)
        bot_reply_text = "I'm here with you. Could you try saying that again?"

    # 3. Save bot reply to DB
    bot_msg = save_message(db, chat_session, sender="bot", content=bot_reply_text)

    # 4. Sync engine state to session draft
    state_summary = engine_manager.get_state_summary(session_id)
    if state_summary:
        update_draft(db, chat_session, state_summary.get("fields_collected", {}))

    # 4b. If the engine just submitted a complaint, create a real DB Complaint
    if (
        state_summary
        and state_summary.get("complaint_submitted")
        and current_user
        and not chat_session.is_submitted
    ):
        fields = state_summary.get("fields_collected", {})
        incident_type = state_summary.get("incident_type") or "general"
        complaint_data = {
            "title": f"{incident_type.replace('_', ' ').title()} Report",
            "category": incident_type,
            "incident_description": fields.get("incident_description", "Filed via Mithuru chatbot"),
            "source_platform": fields.get("platform_name"),
            "victim_name": fields.get("victim_name"),
            "victim_phone": fields.get("victim_phone"),
            "victim_address": fields.get("victim_address"),
            "guardian_phone": fields.get("guardian_phone"),
            "collected_fields": fields,
        }
        try:
            real_complaint = create_chatbot_complaint(db, complaint_data, current_user)
            # Update the engine's tracking_id to match the real case_id
            state_summary["tracking_id"] = real_complaint.case_id
            chat_session.is_submitted = True
            db.commit()
            logger.info("Created DB complaint %s for session %s", real_complaint.case_id, session_id)
        except Exception as exc:
            logger.error("Failed to create DB complaint for session %s: %s", session_id, exc, exc_info=True)

    # 5. Return both messages + state
    return ChatBotReplyResponse(
        user_message=ChatMessageResponse.model_validate(user_msg),
        bot_message=ChatMessageResponse.model_validate(bot_msg),
        mode=state_summary["mode"] if state_summary else "support",
        incident_type=state_summary.get("incident_type") if state_summary else None,
        complaint_submitted=state_summary.get("complaint_submitted", False) if state_summary else False,
        tracking_id=state_summary.get("tracking_id") if state_summary else None,
    )


# ---------------------------------------------------------------------------
# Message history – works for authenticated users AND guests
# ---------------------------------------------------------------------------

@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if current_user:
        chat_session = get_session_or_404(db, session_id, current_user.id)
    else:
        chat_session = get_guest_session_or_404(db, session_id)
    return [ChatMessageResponse.model_validate(m) for m in chat_session.messages]


# ---------------------------------------------------------------------------
# Session state – works for authenticated users AND guests
# ---------------------------------------------------------------------------

@router.get("/sessions/{session_id}/state")
def get_session_state(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if current_user:
        get_session_or_404(db, session_id, current_user.id)
    else:
        get_guest_session_or_404(db, session_id)
    summary = engine_manager.get_state_summary(session_id)
    if not summary:
        return {"mode": "support", "incident_type": None, "complaint_submitted": False, "tracking_id": None}
    return summary


# ---------------------------------------------------------------------------
# Draft & Submit – require authentication
# ---------------------------------------------------------------------------

@router.patch("/sessions/{session_id}/draft")
def patch_draft(
    session_id: str,
    payload: ChatDraftUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_session_or_404(db, session_id, current_user.id)
    updated = update_draft(db, session, payload.draft_data)
    return {"session_id": updated.session_id, "draft_data": updated.draft_data}


@router.post("/sessions/{session_id}/submit", response_model=ComplaintResponse)
def submit_from_chat(
    session_id: str,
    payload: ChatFinalizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_session_or_404(db, session_id, current_user.id)
    return submit_final(db, session, payload, current_user)
