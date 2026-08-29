import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Text, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

class BacktestStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class BacktestRun(Base):
    """Backtest & ROI Simulator Run Record (§34)."""
    __tablename__ = "backtest_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[BacktestStatus] = mapped_column(SQLEnum(BacktestStatus, name="backtest_status_enum"), default=BacktestStatus.PENDING, nullable=False)
    total_dataset_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    simulated_recovered_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    simulated_recovered_revenue_minor: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    simulated_recovery_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    projected_roi_multiplier: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    summary_report: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

class SimulatedActionExecution(Base):
    """Shadow execution record for simulation (§34)."""
    __tablename__ = "simulated_action_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    backtest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    case_reference: Mapped[str] = mapped_column(Text, nullable=False)
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    simulated_decision: Mapped[str] = mapped_column(Text, nullable=False)
    simulated_probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
