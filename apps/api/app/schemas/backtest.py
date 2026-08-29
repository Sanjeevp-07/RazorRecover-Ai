import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.schemas.base import BaseSchema

class BacktestCreateRequest(BaseSchema):
    """Payload to trigger historical simulation replay (§34)."""
    dataset: List[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]] = None

class BacktestResultResponse(BaseSchema):
    """Schema for historical backtesting simulation results (§34)."""
    id: uuid.UUID
    merchant_id: uuid.UUID
    status: str
    total_dataset_cases: int
    simulated_recovered_cases: int
    simulated_recovered_revenue_minor: int
    simulated_recovery_rate: float
    projected_roi_multiplier: float
    summary_report: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
