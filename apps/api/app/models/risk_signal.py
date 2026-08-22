import uuid
from datetime import datetime, timezone
from sqlalchemy import Integer, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class RiskSignal(Base):
    __tablename__ = "risk_signals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recovery_cases.id", ondelete="RESTRICT"), nullable=False, index=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_history_score: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    velocity_flag: Mapped[bool] = mapped_column(Boolean, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
