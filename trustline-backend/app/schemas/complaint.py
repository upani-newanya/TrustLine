from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.core.constants import ComplaintPriorityEnum, ComplaintSourceEnum, ComplaintStatusEnum


class ComplaintCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    category: str = Field(min_length=2, max_length=100)
    incident_description: str = Field(min_length=10)
    source_platform: str | None = Field(default=None, max_length=120)
    incident_date: datetime | None = None
    victim_name: str | None = Field(default=None, max_length=150)
    victim_phone: str | None = Field(default=None, max_length=30)
    victim_address: str | None = Field(default=None, max_length=300)
    guardian_phone: str | None = Field(default=None, max_length=30)


class ComplaintResponse(BaseModel):
    id: int
    case_id: str
    title: str
    category: str
    incident_description: str
    source_platform: str | None
    incident_date: datetime | None
    status: ComplaintStatusEnum
    priority: ComplaintPriorityEnum
    source_type: ComplaintSourceEnum
    reporter_id: int
    assigned_admin_id: int | None
    internal_notes: str | None
    victim_name: str | None = None
    victim_phone: str | None = None
    victim_address: str | None = None
    guardian_phone: str | None = None
    collected_fields: dict[str, Any] | None = None
    reporter_name: str | None = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def fill_reporter_name(self) -> "ComplaintResponse":
        if self.reporter_name is None and self.victim_name:
            self.reporter_name = self.victim_name
        return self

    model_config = {"from_attributes": True}


class ComplaintStatusUpdateRequest(BaseModel):
    status: ComplaintStatusEnum


class ComplaintPriorityUpdateRequest(BaseModel):
    priority: ComplaintPriorityEnum


class ComplaintAssignRequest(BaseModel):
    admin_user_id: int


class ComplaintInternalNoteRequest(BaseModel):
    note: str = Field(min_length=1)
