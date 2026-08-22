import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    ATTEMPTED = "attempted"
    FAILED = "failed"
    CAPTURED = "captured"
    RECOVERED = "recovered"

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="RESTRICT"), nullable=False, index=True)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=True)
    provider_payment_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus, name="payment_status_enum"), nullable=False)
    failure_reason: Mapped[str] = mapped_column(Text, nullable=True)
    method: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
