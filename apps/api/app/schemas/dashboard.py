from typing import List
from app.schemas.base import BaseSchema
from app.schemas.case import RecoveryCaseListItemResponse

class DashboardSummaryResponse(BaseSchema):
    """Dashboard KPIs summary response schema (§1.3 & §19)."""
    failed_revenue_minor: int
    recoverable_revenue_minor: int
    recovered_revenue_minor: int
    recovery_rate: float
    pending_cases: int
    escalations: int
    recent_cases: List[RecoveryCaseListItemResponse]
