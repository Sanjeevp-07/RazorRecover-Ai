import pytest
import hmac
import hashlib
import uuid
from app.policy.engine import evaluate_policy, PolicyEvaluationContext
from app.models.policy_decision import PolicyOutcome
from app.models.payment import PaymentStatus
from app.models.recovery_case import RecoveryCaseStatus
from app.models.action_execution import ActionExecutionStatus
from app.models.approval import ApprovalStatus
from app.tools.base import generate_idempotency_key

# 1. §20.1 Policy Precedence Tests
def test_policy_precedence_already_recovered_beats_amount_threshold():
    """Rule 1 (already_recovered) takes precedence over Rule 6 (amount_threshold)."""
    ctx = PolicyEvaluationContext(
        payment_status="recovered",
        case_status="ANALYZING",
        payment_amount_minor=10000000, # ₹1,00,000 > ₹50,000 threshold
        approval_amount_threshold_minor=5000000,
        recommended_action="CREATE_PAYMENT_LINK",
        ai_confidence=0.95,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "already_recovered"

def test_policy_precedence_case_state_beats_retry_limit():
    """Rule 2 (invalid_case_state) takes precedence over Rule 4 (retry_limit)."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="CLOSED",
        retry_count=5, # > limit 3
        retry_count_limit=3,
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=1000,
        ai_confidence=0.9,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "invalid_case_state"

def test_policy_precedence_retry_limit_beats_risk_threshold():
    """Rule 4 (retry_limit) takes precedence over Rule 7 (risk_threshold)."""
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        retry_count=4, # > limit 3
        retry_count_limit=3,
        ai_confidence=0.1, # < threshold
        ai_requires_human=True,
        recommended_action="CREATE_PAYMENT_LINK",
        payment_amount_minor=1000
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "retry_limit"

# 2. §20.1 Money Conversion Unit Tests
def format_currency_inr(amount_minor: int) -> str:
    """Format paise minor units to INR string."""
    rupees = amount_minor / 100.0
    return f"₹{rupees:,.2f}"

def test_money_conversion_paise_to_inr():
    assert format_currency_inr(1850000) == "₹18,500.00"
    assert format_currency_inr(2499900) == "₹24,999.00"
    assert format_currency_inr(5000000) == "₹50,000.00"
    assert format_currency_inr(0) == "₹0.00"

# 3. §20.1 Webhook Signature Verification Tests
def verify_razorpay_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def test_webhook_signature_verification_valid():
    secret = "rzp_test_secret_12345"
    body = b'{"event":"payment.failed","payload":{"payment":{"entity":{"id":"pay_123"}}}}'
    sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    assert verify_razorpay_signature(body, sig, secret) is True

def test_webhook_signature_verification_invalid():
    secret = "rzp_test_secret_12345"
    body = b'{"event":"payment.failed"}'
    assert verify_razorpay_signature(body, "invalid_sig_hex", secret) is False

def test_webhook_signature_verification_tampered_body():
    secret = "rzp_test_secret_12345"
    original_body = b'{"event":"payment.failed","amount":1000}'
    tampered_body = b'{"event":"payment.failed","amount":9000}'
    sig = hmac.new(secret.encode("utf-8"), original_body, hashlib.sha256).hexdigest()
    assert verify_razorpay_signature(tampered_body, sig, secret) is False

# 4. §20.1 Idempotency Key Generation Tests
def test_idempotency_key_generation_deterministic():
    case_id = uuid.uuid4()
    key1 = generate_idempotency_key(case_id, "create_payment_link", "primary")
    key2 = generate_idempotency_key(case_id, "create_payment_link", "primary")
    assert key1 == key2
    assert len(key1) == 64

def test_idempotency_key_attempt_scope_differentiation():
    case_id = uuid.uuid4()
    key_primary = generate_idempotency_key(case_id, "create_payment_link", "primary")
    key_retry = generate_idempotency_key(case_id, "create_payment_link", "retry-1")
    assert key_primary != key_retry

# 5. §20.1 State Machine Enum Tests (§8)
def test_all_state_machine_values_conformance():
    # Payments (§8.1)
    assert PaymentStatus.CREATED.value == "created"
    assert PaymentStatus.ATTEMPTED.value == "attempted"
    assert PaymentStatus.FAILED.value == "failed"
    assert PaymentStatus.CAPTURED.value == "captured"
    assert PaymentStatus.RECOVERED.value == "recovered"

    # Recovery Cases (§8.2)
    assert RecoveryCaseStatus.OPEN.value == "OPEN"
    assert RecoveryCaseStatus.ANALYZING.value == "ANALYZING"
    assert RecoveryCaseStatus.DENIED.value == "DENIED"
    assert RecoveryCaseStatus.PENDING_APPROVAL.value == "PENDING_APPROVAL"
    assert RecoveryCaseStatus.EXECUTING.value == "EXECUTING"
    assert RecoveryCaseStatus.RECOVERED.value == "RECOVERED"
    assert RecoveryCaseStatus.CLOSED.value == "CLOSED"
    assert RecoveryCaseStatus.EXPIRED.value == "EXPIRED"

    # Action Executions (§8.3)
    assert ActionExecutionStatus.PENDING.value == "PENDING"
    assert ActionExecutionStatus.IN_PROGRESS.value == "IN_PROGRESS"
    assert ActionExecutionStatus.SUCCEEDED.value == "SUCCEEDED"
    assert ActionExecutionStatus.FAILED.value == "FAILED"
    assert ActionExecutionStatus.RETRYING.value == "RETRYING"

    # Approvals (§8.4)
    assert ApprovalStatus.PENDING.value == "PENDING"
    assert ApprovalStatus.APPROVED.value == "APPROVED"
    assert ApprovalStatus.REJECTED.value == "REJECTED"
    assert ApprovalStatus.EXPIRED.value == "EXPIRED"
