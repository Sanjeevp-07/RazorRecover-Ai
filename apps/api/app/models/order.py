import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class OrderStatus(str, enum.Enum):
    CREATED = "created"
    ATTEMPTED = "attempted"
    PAID = "paid"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="RESTRICT"), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=True)
    provider_order_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    amount_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus, name="order_status_enum"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
