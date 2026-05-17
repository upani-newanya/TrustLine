from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import ComplaintPriorityEnum, ComplaintSourceEnum, ComplaintStatusEnum
from app.core.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    incident_description: Mapped[str] = mapped_column(Text, nullable=False)
    incident_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_platform: Mapped[str | None] = mapped_column(String(120), nullable=True)

    victim_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    victim_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    victim_address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    guardian_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    collected_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(String(30), default=ComplaintStatusEnum.PENDING.value, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default=ComplaintPriorityEnum.MEDIUM.value, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), default=ComplaintSourceEnum.MANUAL.value, nullable=False)

    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reporter = relationship("User", back_populates="complaints", foreign_keys=[reporter_id])
    assigned_admin = relationship("User", back_populates="assigned_complaints", foreign_keys=[assigned_admin_id])

    evidence_items = relationship("Evidence", back_populates="complaint", cascade="all, delete-orphan")
    messages = relationship("ComplaintMessage", back_populates="complaint", cascade="all, delete-orphan")
