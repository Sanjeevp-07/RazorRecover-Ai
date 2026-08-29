import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.schemas.base import BaseSchema
from app.models.recovery_case import RecoveryCaseStatus

class PaymentSummarySchema(BaseSchema):
    id: uuid.UUID
    amount_minor: int
    currency: str
    status: str
    failure_class: Optional[str] = "UNKNOWN"
    failure_reason: Optional[str] = None
    method: Optional[str] = None

class RiskSignalsSummarySchema(BaseSchema):
    retry_count: int
    customer_history_score: float
    velocity_flag: bool

class AIDecisionSummarySchema(BaseSchema):
    recommended_action: str
    recovery_probability: float
    confidence: float
    requires_human: bool
    reason: str
    probability_source: Optional[str] = "llm"
    schema_version: str

class PolicyDecisionSummarySchema(BaseSchema):
    decision: str
    matched_rule: str
    matched_rule_human: Optional[str] = None
    policy_mode: Optional[str] = "sequential_threshold"
    policy_version: str

class ApprovalSummarySchema(BaseSchema):
    status: str
    sla_expires_at: datetime

class RecoveryCaseDetailResponse(BaseSchema):
    """Full recovery case detail response schema (§9.2 & §37)."""
    id: uuid.UUID
    status: RecoveryCaseStatus
    expected_value_minor: Optional[int] = 0
    payment: PaymentSummarySchema
    risk_signals: Optional[RiskSignalsSummarySchema] = None
    ai_decision: Optional[AIDecisionSummarySchema] = None
    policy_decision: Optional[PolicyDecisionSummarySchema] = None
    approval: Optional[ApprovalSummarySchema] = None
    explainability: Optional[Dict[str, Any]] = None

class RecoveryCaseListItemResponse(BaseSchema):
    """Paginated case list item response."""
    id: uuid.UUID
    merchant_id: uuid.UUID
    payment_id: uuid.UUID
    status: RecoveryCaseStatus
    correlation_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class AuditLogTimelineItem(BaseSchema):
    """Ordered audit log timeline item (§9.2)."""
    id: uuid.UUID
    merchant_id: uuid.UUID
    correlation_id: uuid.UUID
    event_type: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime
