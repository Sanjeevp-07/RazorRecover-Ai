from typing import List
from app.schemas.base import BaseSchema

class ReasonBreakdown(BaseSchema):
    reason: str
    count: int
    recovered_count: int
    amount_minor: int
    recovered_amount_minor: int
    rate: float

class ActionBreakdown(BaseSchema):
    action: str
    count: int
    percentage: float

class TrendDay(BaseSchema):
    day: str
    total_volume: float
    recovered_volume: float
    baseline_rate: float
    ai_rate: float

class AnalyticsPerformanceResponse(BaseSchema):
    total_failed_revenue_minor: int
    recoverable_revenue_minor: int
    recovered_revenue_minor: int
    recovery_rate: float
    prevented_fraud_minor: int
    total_cases: int
    recovered_cases: int
    pending_cases: int
    escalations: int
    avg_latency_hours: float
    benchmark_baseline_rate: float
    reason_breakdowns: List[ReasonBreakdown]
    action_breakdowns: List[ActionBreakdown]
    trend_progression: List[TrendDay]
