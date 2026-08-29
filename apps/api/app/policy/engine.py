from typing import Optional, Set
from pydantic import BaseModel
from app.models.policy_decision import PolicyOutcome

# List of actions supported by implemented tools (§13.1 Rule 5 & §14)
SUPPORTED_TOOL_ACTIONS: Set[str] = {
    "CREATE_PAYMENT_LINK",
    "CREATE_RESUME_SESSION",
    "SEND_NOTIFICATION",
    "RETRY_PAYMENT",
    "ESCALATE_CASE",
    "NO_ACTION"
}

class PolicyEvaluationContext(BaseModel):
    """Context required for pure-function policy evaluation (§13.1, §38 & §41)."""
    payment_status: str
    case_status: str
    existing_action_statuses: Set[str] = set()
    retry_count: int = 0
    velocity_flag: bool = False
    recommended_action: str
    payment_amount_minor: int
    ai_confidence: float
    ai_requires_human: bool
    
    # Policy evaluation mode (§38): 'sequential_threshold' (default) or 'risk_matrix'
    policy_mode: str = "sequential_threshold"

    # Configurable thresholds (§6.11, §13.2 & §38)
    retry_count_limit: int = 3
    approval_amount_threshold_minor: int = 5000000  # Default ₹50,000
    approval_risk_threshold: float = 0.7            # Default 0.7 risk threshold

class PolicyDecisionResult(BaseModel):
    """Result of policy evaluation."""
    decision: PolicyOutcome
    matched_rule: str
    policy_version: str = "3.0"

def evaluate_policy(ctx: PolicyEvaluationContext) -> PolicyDecisionResult:
    """
    Pure deterministic Policy Evaluation Engine (§13.1, §38 & §41).
    Evaluated top-to-bottom; FIRST matching rule decides and stops.
    No I/O.
    """
    # 1. Payment state check (§41 Rule 1)
    if ctx.payment_status.lower() in ("captured", "recovered"):
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="already_recovered"
        )

    # 2. Case state check (§41 Rule 2)
    if ctx.case_status.upper() != "ANALYZING":
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="invalid_case_state"
        )

    # 3. Duplicate action check (§41 Rule 3)
    if any(s.upper() in ("PENDING", "SUCCEEDED") for s in ctx.existing_action_statuses):
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="duplicate_action"
        )

    # 4. Velocity / Abuse check (§33 & §41 Rule 4)
    if ctx.velocity_flag:
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="velocity_abuse_suspected"
        )

    # 5. Retry limit check (§41 Rule 5)
    if ctx.retry_count > ctx.retry_count_limit:
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="retry_limit"
        )

    # 6. Provider capability check (§41 Rule 6)
    if ctx.recommended_action not in SUPPORTED_TOOL_ACTIONS:
        return PolicyDecisionResult(
            decision=PolicyOutcome.DENY,
            matched_rule="unsupported_action"
        )

    # 7 & 8. Threshold / Risk Matrix Evaluation (§38 & §41 Rule 7 & 8)
    min_confidence = round(1.0 - ctx.approval_risk_threshold, 3)

    if ctx.policy_mode == "risk_matrix":
        # 2D Amount Band x Confidence Band Risk Matrix (§38)
        is_high_amount = ctx.payment_amount_minor > ctx.approval_amount_threshold_minor
        is_high_confidence = (ctx.ai_confidence >= 0.75) and not ctx.ai_requires_human
        is_low_confidence = (ctx.ai_confidence < min_confidence) or ctx.ai_requires_human

        if is_high_amount and is_high_confidence:
            # High amount + Very high confidence -> ALLOW in risk matrix mode
            return PolicyDecisionResult(
                decision=PolicyOutcome.ALLOW,
                matched_rule="risk_matrix_high_value_high_confidence"
            )
        elif is_high_amount:
            # High amount without high confidence -> force review
            return PolicyDecisionResult(
                decision=PolicyOutcome.HUMAN_APPROVAL,
                matched_rule="risk_matrix_high_value_review"
            )
        elif is_low_confidence:
            # Low confidence on low/medium amount -> review
            return PolicyDecisionResult(
                decision=PolicyOutcome.HUMAN_APPROVAL,
                matched_rule="risk_matrix_low_confidence_review"
            )
        else:
            # Normal amount + medium/high confidence -> ALLOW
            return PolicyDecisionResult(
                decision=PolicyOutcome.ALLOW,
                matched_rule="risk_matrix_allow"
            )
    else:
        # Default Sequential Thresholds (§13.1 & §41)
        # 7. Amount threshold check
        if ctx.payment_amount_minor > ctx.approval_amount_threshold_minor:
            return PolicyDecisionResult(
                decision=PolicyOutcome.HUMAN_APPROVAL,
                matched_rule="amount_threshold"
            )

        # 8. Risk threshold check
        if ctx.ai_confidence < min_confidence or ctx.ai_requires_human:
            return PolicyDecisionResult(
                decision=PolicyOutcome.HUMAN_APPROVAL,
                matched_rule="risk_threshold"
            )

    # 9. Default ALLOW (§41 Rule 9)
    return PolicyDecisionResult(
        decision=PolicyOutcome.ALLOW,
        matched_rule="default_allow"
    )
