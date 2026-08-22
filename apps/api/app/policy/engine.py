from typing import Optional, Set
from pydantic import BaseModel
from app.models.policy_decision import PolicyOutcome

# List of actions supported by implemented tools (§13.1 Rule 5 & §14)
SUPPORTED_TOOL_ACTIONS: Set[str] = {
    "CREATE_PAYMENT_LINK",
    "SEND_NOTIFICATION",
    "RETRY_PAYMENT",
    "ESCALATE_CASE",
    "NO_ACTION"
}

class PolicyEvaluationContext(BaseModel):
    """Context required for pure-function policy evaluation (§13.1)."""
    payment_status: str
    case_status: str
    existing_action_statuses: Set[str] = set()
    retry_count: int = 0
    recommended_action: str
    payment_amount_minor: int
    ai_confidence: float
    ai_requires_human: bool
    
    # Configurable thresholds (§6.11 & §13.2)
    retry_count_limit: int = 3
    approval_amount_threshold_minor: int = 5000000  # Default ₹50,000
    approval_risk_threshold: float = 0.7            # Default 0.7 risk threshold

class PolicyDecisionResult(BaseModel):
    """Result of policy evaluation."""
    decision: PolicyOutcome
    matched_rule: str
    policy_version: str = "1.0"

def evaluate_policy(ctx: PolicyEvaluationContext) -> PolicyDecisionResult:
    """
    Pure deterministic Policy Evaluation Engine (§13.1).
    Evaluated top-to-bottom; FIRST matching rule decides and stops.
    No I/O.
    """
    # 1. Payment state check (§13.1 Rule 1)
    if ctx.payment_status.lower() in ("captured", "recovered"):
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="already_recovered"
        )

    # 2. Case state check (§13.1 Rule 2)
    if ctx.case_status.upper() != "ANALYZING":
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="invalid_case_state"
        )

    # 3. Duplicate action check (§13.1 Rule 3)
    if any(s.upper() in ("PENDING", "SUCCEEDED") for s in ctx.existing_action_statuses):
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="duplicate_action"
        )

    # 4. Retry limit check (§13.1 Rule 4)
    if ctx.retry_count > ctx.retry_count_limit:
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="retry_limit"
        )

    # 5. Provider capability check (§13.1 Rule 5)
    if ctx.recommended_action not in SUPPORTED_TOOL_ACTIONS:
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="unsupported_action"
        )

    # 6. Amount threshold check (§13.1 Rule 6)
    if ctx.payment_amount_minor > ctx.approval_amount_threshold_minor:
        return PolicyDecisionResult(
            decision=PolicyOutcome.HUMAN_APPROVAL,
            matched_rule="amount_threshold"
        )

    # 7. Risk threshold check (§13.1 Rule 7)
    # Risk threshold condition: confidence < (1 - risk_threshold) OR requires_human == True
    min_confidence = round(1.0 - ctx.approval_risk_threshold, 3)
    if ctx.ai_confidence < min_confidence or ctx.ai_requires_human:
        return PolicyDecisionResult(
            decision=PolicyOutcome.HUMAN_APPROVAL,
            matched_rule="risk_threshold"
        )

    # 8. Default ALLOW (§13.1 Rule 8)
    return PolicyDecisionResult(
        decision=PolicyOutcome.ALLOW,
        matched_rule="default_allow"
    )
