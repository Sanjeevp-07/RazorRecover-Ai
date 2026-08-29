import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class RecoveryCaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    ANALYZING = "ANALYZING"
    DENIED = "DENIED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    EXECUTING = "EXECUTING"
    RECOVERED = "RECOVERED"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"

class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="RESTRICT"), nullable=False, index=True)
    payment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[RecoveryCaseStatus] = mapped_column(SQLEnum(RecoveryCaseStatus, name="recovery_case_status_enum"), default=RecoveryCaseStatus.OPEN, nullable=False, index=True)
    expected_value_minor: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correlation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
