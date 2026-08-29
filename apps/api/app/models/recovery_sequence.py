import uuid
from datetime import datetime, timezone
from sqlalchemy import Text, Integer, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class RecoverySequence(Base):
    """Merchant-editable multi-step recovery playbook (§31)."""
    __tablename__ = "recovery_sequences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    failure_class: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class RecoverySequenceStep(Base):
    """Step in a multi-step recovery playbook (§31)."""
    __tablename__ = "recovery_sequence_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sequence_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recovery_sequences.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    day_offset: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    channel: Mapped[str] = mapped_column(Text, default="WHATSAPP", nullable=False)
    template_name: Mapped[str] = mapped_column(Text, nullable=False)
    conditions: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
