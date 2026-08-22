import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class PolicyOutcome(str, enum.Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"

class PolicyDecision(Base):
    __tablename__ = "policy_decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recovery_cases.id", ondelete="RESTRICT"), nullable=False, index=True)
    ai_decision_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_decisions.id", ondelete="RESTRICT"), nullable=True)
    decision: Mapped[PolicyOutcome] = mapped_column(SQLEnum(PolicyOutcome, name="policy_outcome_enum"), nullable=False)
    policy_version: Mapped[str] = mapped_column(Text, nullable=False)
    matched_rule: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
