import uuid
from datetime import datetime, timezone
from sqlalchemy import Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="RESTRICT"), nullable=False, index=True)
    correlation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
