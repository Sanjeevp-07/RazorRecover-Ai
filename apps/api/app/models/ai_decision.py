import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class ProbabilitySource(str, enum.Enum):
    BASELINE_MODEL = "baseline_model"
    LLM = "llm"
    ENSEMBLE = "ensemble"

class AIDecision(Base):
    __tablename__ = "ai_decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recovery_cases.id", ondelete="RESTRICT"), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(Text, nullable=False)
    schema_version: Mapped[str] = mapped_column(Text, nullable=False)
    probability_source: Mapped[ProbabilitySource] = mapped_column(SQLEnum(ProbabilitySource, name="probability_source_enum"), default=ProbabilitySource.LLM, nullable=False)
    raw_output: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    validated_output: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
