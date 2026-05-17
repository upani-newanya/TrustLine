from datetime import datetime

from pydantic import BaseModel


class EvidenceResponse(BaseModel):
    id: int
    complaint_id: int
    uploaded_by: int
    original_file_name: str
    stored_file_name: str
    file_path: str
    file_type: str
    mime_type: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}
