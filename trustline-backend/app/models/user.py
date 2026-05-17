from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import RoleEnum
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=RoleEnum.USER.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    guardian_id: Mapped[int | None] = mapped_column(ForeignKey("guardian_profiles.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    guardian_profile = relationship("GuardianProfile", back_populates="users")
    admin_profile = relationship("AdminProfile", back_populates="user", uselist=False)

    complaints = relationship("Complaint", back_populates="reporter", foreign_keys="Complaint.reporter_id")
    assigned_complaints = relationship("Complaint", back_populates="assigned_admin", foreign_keys="Complaint.assigned_admin_id")
    evidence_items = relationship("Evidence", back_populates="uploader")
