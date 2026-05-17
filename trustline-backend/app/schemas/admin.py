from pydantic import BaseModel


class AdminDashboardResponse(BaseModel):
    total_complaints: int
    pending_count: int
    under_review_count: int
    need_more_info_count: int
    escalated_count: int
    closed_count: int


class AdminQueueItemResponse(BaseModel):
    id: int
    case_id: str
    title: str
    category: str
    status: str
    priority: str
    created_at: str
