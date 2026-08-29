import pytest
import uuid
from app.models.failure_taxonomy import FailureClass
from app.models.policy_decision import PolicyOutcome
from app.ai.baseline_scorer import BaselineScorer
from app.ai.circuit_breaker import AICircuitBreaker
from app.tools.resume_session_tool import CreateResumeSessionTool
from app.policy.engine import evaluate_policy, PolicyEvaluationContext

def test_baseline_scorer_heuristic_and_adjustments():
    # Customer history score 0.8, retry count 1, INSUFFICIENT_FUNDS (+0.15)
    # Expected: 0.5 + 0.3*0.8 - 0.1*1 + 0.15 = 0.5 + 0.24 - 0.1 + 0.15 = 0.79
    res = BaselineScorer.calculate_baseline(
        customer_history_score=0.8,
        retry_count=1,
        velocity_flag=False,
        failure_class=FailureClass.INSUFFICIENT_FUNDS
    )
    assert res.baseline_probability == 0.79
    assert res.recommended_action == "CREATE_PAYMENT_LINK"
    assert not res.is_in_gray_zone

def test_baseline_scorer_otp_abandoned():
    res = BaselineScorer.calculate_baseline(
        customer_history_score=0.7,
        retry_count=1,
        velocity_flag=False,
        failure_class=FailureClass.OTP_3DS_ABANDONED
    )
    assert res.recommended_action == "CREATE_RESUME_SESSION"
    assert "Mid-funnel dropoff" in res.reason

def test_baseline_scorer_gray_zone_detection():
    # History 0.5, retry 2, UNKNOWN (0.0 adj)
    # Expected: 0.5 + 0.15 - 0.2 = 0.45 (in [0.35, 0.65])
    res = BaselineScorer.calculate_baseline(
        customer_history_score=0.5,
        retry_count=2,
        velocity_flag=False,
        failure_class=FailureClass.UNKNOWN
    )
    assert res.baseline_probability == 0.45
    assert res.is_in_gray_zone is True

def test_ai_circuit_breaker_tripping_and_cooldown():
    cb = AICircuitBreaker(failure_threshold=3, cooldown_minutes=15)
    assert not cb.is_tripped()

    cb.record_failure()
    cb.record_failure()
    assert not cb.is_tripped()

    cb.record_failure() # 3rd failure -> trips breaker
    assert cb.is_tripped()

    cb.reset()
    assert not cb.is_tripped()

@pytest.mark.asyncio
async def test_create_resume_session_tool():
    tool = CreateResumeSessionTool(base_checkout_url="https://shop.example.com/checkout/resume")
    case_id = uuid.uuid4()
    success, output, error = await tool.execute(case_id=case_id, payload={})

    assert success is True
    assert error == ""
    assert "resume_url" in output
    assert str(case_id) in output["resume_url"]
    assert output["type"] == "RESUME_CHECKOUT_SESSION"
    assert output["status"] == "active"

def test_policy_engine_velocity_abuse_denial():
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        existing_action_statuses=set(),
        retry_count=1,
        velocity_flag=True, # Velocity flag active
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=150000,
        ai_confidence=0.85,
        ai_requires_human=False
    )
    result = evaluate_policy(ctx)
    assert result.decision == PolicyOutcome.DENY
    assert result.matched_rule == "velocity_abuse_suspected"

def test_policy_engine_resume_session_allow():
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        existing_action_statuses=set(),
        retry_count=1,
        velocity_flag=False,
        recommended_action="CREATE_RESUME_SESSION",
        payment_amount_minor=200000,
        ai_confidence=0.90,
        ai_requires_human=False
    )
    result = evaluate_policy(ctx)
    assert result.decision == PolicyOutcome.ALLOW
    assert result.matched_rule == "default_allow"
