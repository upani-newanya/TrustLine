from enum import Enum


class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"
    GUARDIAN = "guardian"


class ComplaintStatusEnum(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    NEED_MORE_INFO = "need_more_info"
    ESCALATED = "escalated"
    CLOSED = "closed"


class ComplaintPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ComplaintSourceEnum(str, Enum):
    MANUAL = "manual"
    CHATBOT = "chatbot"


class EvidenceTypeEnum(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
#evedance type need to add urls