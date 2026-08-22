import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recovery_cases.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[ApprovalStatus] = mapped_column(SQLEnum(ApprovalStatus, name="approval_status_enum"), default=ApprovalStatus.PENDING, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    sla_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decided_by_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchant_users.id", ondelete="RESTRICT"), nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_note: Mapped[str] = mapped_column(Text, nullable=True)
