from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserProfileResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone_number: str | None
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
