import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class CohortType(str, enum.Enum):
    TREATMENT = "treatment"
    CONTROL = "control"

class ExperimentAssignment(Base):
    __tablename__ = "experiment_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recovery_cases.id", ondelete="RESTRICT"), nullable=False, index=True)
    cohort: Mapped[CohortType] = mapped_column(SQLEnum(CohortType, name="cohort_type_enum"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    eligibility_reason: Mapped[str] = mapped_column(Text, nullable=True)
