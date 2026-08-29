import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ActionExecutionStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    SUPPRESSED_CONTROL = "SUPPRESSED_CONTROL"

class ActionExecution(Base):
    __tablename__ = "action_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recovery_cases.id", ondelete="RESTRICT"), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    status: Mapped[ActionExecutionStatus] = mapped_column(SQLEnum(ActionExecutionStatus, name="action_execution_status_enum"), default=ActionExecutionStatus.PENDING, nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSONB, nullable=True)
    output_payload: Mapped[dict] = mapped_column(JSONB, nullable=True)
    error_category: Mapped[str] = mapped_column(Text, nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
