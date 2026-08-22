import uuid
from typing import List, Literal
import enum
from pydantic import Field
from app.schemas.base import BaseSchema

class RecommendedAction(str, enum.Enum):
    CREATE_PAYMENT_LINK = "CREATE_PAYMENT_LINK"
    SEND_NOTIFICATION = "SEND_NOTIFICATION"
    RETRY_PAYMENT = "RETRY_PAYMENT"
    ESCALATE_CASE = "ESCALATE_CASE"
    NO_ACTION = "NO_ACTION"

class RecoveryRecommendation(BaseSchema):
    """
    AI Output JSON Schema (schema_version 1.0 — §12.1).
    Strict schema contract enforced via Pydantic extra="forbid" and OpenAI Structured Outputs.
    """
    schema_version: Literal["1.0"] = Field("1.0", description="Schema version identifier")
    case_id: uuid.UUID = Field(..., description="Target recovery case UUID")
    recovery_probability: float = Field(..., ge=0.0, le=1.0, description="Estimated recovery probability between 0 and 1")
    recommended_action: RecommendedAction = Field(..., description="Action recommendation label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score between 0 and 1")
    requires_human: bool = Field(..., description="Whether human approval is required")
    reason: str = Field(..., max_length=400, description="Concise rationale for recommendation")
    risk_signals: List[str] = Field(..., max_length=10, description="List of observed risk signals")
