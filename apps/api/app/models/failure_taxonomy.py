import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class FailureClass(str, enum.Enum):
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    OTP_3DS_ABANDONED = "OTP_3DS_ABANDONED"
    ISSUER_RISK_DECLINE = "ISSUER_RISK_DECLINE"
    GATEWAY_BANK_TIMEOUT = "GATEWAY_BANK_TIMEOUT"
    EXPIRED_OR_INVALID_INSTRUMENT = "EXPIRED_OR_INVALID_INSTRUMENT"
    VPA_INVALID = "VPA_INVALID"
    UNKNOWN = "UNKNOWN"

class FailureTaxonomyMap(Base):
    __tablename__ = "failure_taxonomy_map"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    failure_class: Mapped[FailureClass] = mapped_column(SQLEnum(FailureClass, name="failure_class_enum"), nullable=False, unique=True)
    error_reason_patterns: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    error_source_patterns: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    error_step_patterns: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    default_channel: Mapped[str] = mapped_column(Text, default="WHATSAPP", nullable=False)
    default_delay_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    default_tone: Mapped[str] = mapped_column(Text, default="empathetic", nullable=False)
    native_retry_grace_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
