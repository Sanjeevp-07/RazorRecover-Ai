import uuid
from datetime import datetime, timezone
from sqlalchemy import Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class CustomerCommunicationPreference(Base):
    """Customer communication consent & DPDP preferences (§35)."""
    __tablename__ = "customer_communication_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(Text, nullable=False) # e.g. "WHATSAPP", "EMAIL", "SMS"
    opt_in: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, default="payment_recovery_outreach", nullable=False)
    consent_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
