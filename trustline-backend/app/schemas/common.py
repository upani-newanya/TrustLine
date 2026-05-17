from datetime import datetime

from pydantic import BaseModel


class APIMessage(BaseModel):
    message: str


class TimestampMixin(BaseModel):
    created_at: datetime
