from datetime import datetime

from pydantic import BaseModel, Field


class ComplaintMessageCreateRequest(BaseModel):
    body: str = Field(min_length=1)


class ComplaintMessageResponse(BaseModel):
    id: int
    complaint_id: int
    sender_id: int
    body: str
    is_internal: bool
    created_at: datetime

    model_config = {"from_attributes": True}
