from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatSessionStartResponse(BaseModel):
    session_id: str


class ChatMessageCreateRequest(BaseModel):
    content: str = Field(min_length=1)


class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatBotReplyResponse(BaseModel):
    """Response returned after sending a message — includes bot reply + state."""
    user_message: ChatMessageResponse
    bot_message: ChatMessageResponse
    mode: str
    incident_type: Optional[str] = None
    complaint_submitted: bool = False
    tracking_id: Optional[str] = None


class ChatDraftUpdateRequest(BaseModel):
    draft_data: dict


class ChatFinalizeRequest(BaseModel):
    title: str
    category: str
    incident_description: str
    source_platform: str | None = None
