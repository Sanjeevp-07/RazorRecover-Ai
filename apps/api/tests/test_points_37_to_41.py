import uuid
import pytest
from app.policy.engine import evaluate_policy, PolicyEvaluationContext
from app.models.policy_decision import PolicyOutcome
from app.services.recovery_case_service import get_rule_human_explanation, RULE_EXPLANATIONS
from app.models.experiment_assignment import CohortType
from app.models.action_execution import ActionExecutionStatus

# -----------------------------------------------------------------------------
# Point 37: Explainability & Trust Layer Tests
# -----------------------------------------------------------------------------
def test_point_37_get_rule_human_explanation():
    """Verify human readable explanations exist for all policy rules."""
    assert "amount_threshold" in RULE_EXPLANATIONS
    assert "risk_threshold" in RULE_EXPLANATIONS
    assert "velocity_abuse_suspected" in RULE_EXPLANATIONS
    assert "already_recovered" in RULE_EXPLANATIONS
    assert "risk_matrix_high_value_high_confidence" in RULE_EXPLANATIONS

    exp = get_rule_human_explanation("amount_threshold")
    assert "₹50,000" in exp or "High Transaction Value" in exp

    fallback_exp = get_rule_human_explanation("custom_rule_abc")
    assert fallback_exp == "Deterministic guardrail evaluated: custom_rule_abc"


# -----------------------------------------------------------------------------
# Point 38: Configurable Policy Engine Evaluation Modes (v3 & Risk Matrix)
# -----------------------------------------------------------------------------
def test_point_38_risk_matrix_mode_high_val_high_conf():
    """Point 38: Risk Matrix Mode allows high value when confidence is high."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        policy_mode="risk_matrix",
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=7500000,  # ₹75,000 (> ₹50,000)
        approval_amount_threshold_minor=5000000,
        ai_confidence=0.88,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.ALLOW
    assert res.matched_rule == "risk_matrix_high_value_high_confidence"

def test_point_38_risk_matrix_mode_high_val_low_conf():
    """Point 38: Risk Matrix Mode requires approval for high value with moderate confidence."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        policy_mode="risk_matrix",
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=7500000,
        approval_amount_threshold_minor=5000000,
        ai_confidence=0.65,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.HUMAN_APPROVAL
    assert res.matched_rule == "risk_matrix_high_value_review"


# -----------------------------------------------------------------------------
# Point 39: Control Cohort Suppression Logic
# -----------------------------------------------------------------------------
def test_point_39_control_cohort_enums():
    """Point 39: Verify cohort types and suppressed control action status."""
    assert CohortType.CONTROL.value == "control"
    assert CohortType.TREATMENT.value == "treatment"
    assert ActionExecutionStatus.SUPPRESSED_CONTROL.value == "SUPPRESSED_CONTROL"


# -----------------------------------------------------------------------------
# Point 40: Backtest & Customer Preference API Schemas
# -----------------------------------------------------------------------------
def test_point_40_customer_preference_schema():
    """Point 40: Verify customer communication preference schemas."""
    from datetime import datetime, timezone
    from app.schemas.preferences import CommunicationPreferenceUpdate, CommunicationPreferenceResponse
    pref_update = CommunicationPreferenceUpdate(
        channel="WHATSAPP",
        opt_in=False,
        purpose="payment_recovery_outreach"
    )
    assert pref_update.channel == "WHATSAPP"
    assert pref_update.opt_in is False

    pref_resp = CommunicationPreferenceResponse(
        id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        channel="SMS",
        opt_in=True,
        purpose="payment_recovery_outreach",
        consent_timestamp=datetime.now(timezone.utc)
    )
    assert pref_resp.channel == "SMS"
    assert pref_resp.opt_in is True


# -----------------------------------------------------------------------------
# Point 41: Updated Policy Engine — Ordered Evaluation (v3 Precedence)
# -----------------------------------------------------------------------------
def test_point_41_ordered_evaluation_precedence():
    """
    Point 41: Top-to-bottom rule ordering test.
    Rule 1 (already_recovered) MUST take precedence over Rule 4 (velocity_flag).
    """
    ctx = PolicyEvaluationContext(
        payment_status="captured",  # Rule 1 trigger
        case_status="ANALYZING",
        velocity_flag=True,         # Rule 4 trigger
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=1000,
        ai_confidence=0.9,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    # Rule 1 matches FIRST and halts evaluation
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "already_recovered"

def test_point_41_rule_ordering_velocity_over_unsupported_action():
    """
    Rule 4 (velocity_abuse_suspected) MUST take precedence over Rule 6 (unsupported_action).
    """
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        velocity_flag=True,                         # Rule 4 trigger
        recommended_action="INVALID_UNSUPPORTED",   # Rule 6 trigger
        payment_amount_minor=1000,
        ai_confidence=0.9,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "velocity_abuse_suspected"
