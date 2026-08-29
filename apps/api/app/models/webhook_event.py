import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class WebhookProcessingStatus(str, enum.Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="RESTRICT"), nullable=False, index=True)
    external_event_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    processing_status: Mapped[WebhookProcessingStatus] = mapped_column(SQLEnum(WebhookProcessingStatus, name="webhook_processing_status_enum"), default=WebhookProcessingStatus.RECEIVED, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
