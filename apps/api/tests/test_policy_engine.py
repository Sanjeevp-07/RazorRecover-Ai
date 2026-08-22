import pytest
from app.policy.engine import evaluate_policy, PolicyEvaluationContext
from app.models.policy_decision import PolicyOutcome

def test_policy_rule_1_already_recovered_payment_denied():
    """Rule 1: Payment state is already captured or recovered -> DENY (already_recovered)."""
    ctx = PolicyEvaluationContext(
        payment_status="recovered",
        case_status="ANALYZING",
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=1000,
        ai_confidence=0.9,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "already_recovered"

def test_policy_rule_2_invalid_case_state_denied():
    """Rule 2: Case state is not ANALYZING -> DENY (invalid_case_state)."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="CLOSED",
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=1000,
        ai_confidence=0.9,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "invalid_case_state"

def test_policy_rule_3_duplicate_action_denied():
    """Rule 3: Duplicate action PENDING or SUCCEEDED -> DENY (duplicate_action)."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        existing_action_statuses={"SUCCEEDED"},
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=1000,
        ai_confidence=0.9,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "duplicate_action"

def test_policy_rule_4_retry_limit_exceeded_denied():
    """Rule 4: retry_count > limit -> DENY (retry_limit)."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        retry_count=4,
        retry_count_limit=3,
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=1000,
        ai_confidence=0.9,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "retry_limit"

def test_policy_rule_5_unsupported_action_denied():
    """Rule 5: recommended_action not in supported tool set -> DENY (unsupported_action)."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        recommended_action="UNKNOWN_UNSUPPORTED_ACTION",
        payment_amount_minor=1000,
        ai_confidence=0.9,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "unsupported_action"

def test_policy_rule_6_amount_threshold_human_approval():
    """Rule 6: payment_amount_minor > threshold -> HUMAN_APPROVAL (amount_threshold)."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=6000000,  # ₹60,000 > ₹50,000 limit
        approval_amount_threshold_minor=5000000,
        ai_confidence=0.95,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.HUMAN_APPROVAL
    assert res.matched_rule == "amount_threshold"

def test_policy_rule_7_risk_threshold_human_approval():
    """Rule 7: ai_confidence low or ai_requires_human -> HUMAN_APPROVAL (risk_threshold)."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=1000,
        ai_confidence=0.1,  # Low confidence < (1 - 0.7 = 0.3)
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.HUMAN_APPROVAL
    assert res.matched_rule == "risk_threshold"

def test_policy_rule_8_default_allow():
    """Rule 8: All checks pass -> ALLOW (default_allow)."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=1000,
        ai_confidence=0.95,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.ALLOW
    assert res.matched_rule == "default_allow"
