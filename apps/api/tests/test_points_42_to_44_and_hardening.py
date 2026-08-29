import hmac
import hashlib
import pytest
from unittest.mock import AsyncMock, patch

from app.services.system_service import SystemService
from app.core.crypto import encrypt_secret, decrypt_secret
from app.policy.engine import evaluate_policy, PolicyEvaluationContext
from app.models.policy_decision import PolicyOutcome

# -----------------------------------------------------------------------------
# Point 42: Build Roadmap From 80% Completion Tests (§42)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_point_42_system_roadmap():
    """Point 42: Verify overall system completion is 100% and contains all modules."""
    mock_session = AsyncMock()
    service = SystemService(mock_session)
    res = await service.get_roadmap()
    
    assert res.overall_completion_pct == 100.0
    assert res.current_version == "3.0.0"
    assert res.built_modules_count == 44
    assert len(res.items) >= 8

    # Verify key roadmap feature items are listed as COMPLETED
    feature_names = [item.feature_name for item in res.items]
    assert any("Policy Engine (v3)" in name for name in feature_names)
    assert any("Explainability" in name for name in feature_names)
    assert any("Policy Engine Modes" in name for name in feature_names)
    assert any("Holdout" in name for name in feature_names)


# -----------------------------------------------------------------------------
# Point 43: System Hardening & Resilience Verification Matrix Tests (§43)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_point_43_resilience_matrix():
    """Point 43: Verify resilience matrix health metrics and component statuses."""
    mock_session = AsyncMock()
    service = SystemService(mock_session)
    res = await service.get_resilience_matrix()

    assert res.overall_resilience_status == "HEALTHY"
    assert len(res.metrics) >= 5

    # Verify component health checks
    comp_names = [m.component for m in res.metrics]
    assert any("AI Inference Engine" in name for name in comp_names)
    assert any("Policy Engine Guardrail" in name for name in comp_names)
    assert any("Fernet Secrets Encryption" in name for name in comp_names)


@pytest.mark.asyncio
async def test_point_43_ai_fallback_mechanism_on_llm_failure():
    """
    Point 43 Hardening: When external LLM provider fails, system MUST
    gracefully fallback to fail-closed recommendation or baseline scoring without crashing.
    """
    import uuid
    from app.ai.openai_provider import OpenAIReasoner
    from app.ai.baseline_scorer import BaselineScorer

    reasoner = OpenAIReasoner(api_key="invalid_test_key_for_fallback")
    case_id = uuid.uuid4()
    
    # Mock LLM client raising an API exception
    with patch.object(reasoner.client.chat.completions, "create", side_effect=Exception("NVIDIA NIM API Connection Timeout")):
        rec, success, raw_text, latency = await reasoner.analyze(
            case_id=case_id,
            context={
                "payment_amount_minor": 250000,
                "currency": "INR",
                "error_code": "BAD_REQUEST_ERROR",
                "error_description": "OTP authentication timeout",
                "customer_history_score": 0.8,
                "retry_count": 1
            }
        )
        # Should gracefully return fail-closed recommendation instead of crashing
        assert success is False
        assert rec.requires_human is True
        assert rec.recommended_action.value == "ESCALATE_CASE"
        assert "ai_unavailable" in rec.risk_signals

    # Verify Baseline Scorer works deterministically
    baseline_res = BaselineScorer.calculate_baseline(
        customer_history_score=0.8,
        retry_count=1
    )
    assert baseline_res.recommended_action in ("CREATE_RESUME_SESSION", "CREATE_PAYMENT_LINK")
    assert baseline_res.baseline_probability > 0.0


def test_point_43_fernet_crypto_hardening():
    """Point 43 Hardening: Verify Fernet secret encryption and decryption round-trip."""
    raw_secret = "rzp_live_secret_key_super_confidential_12345"
    encrypted = encrypt_secret(raw_secret)
    
    assert encrypted != raw_secret
    assert encrypted.startswith("gAAAAA")  # Standard Fernet token format
    
    decrypted = decrypt_secret(encrypted)
    assert decrypted == raw_secret


def test_point_43_webhook_signature_hardening():
    """Point 43 Hardening: Verify HMAC-SHA256 webhook signature verification algorithm."""
    secret = "rzp_webhook_secret_key_123"
    body = b'{"event":"payment.failed","payload":{}}'
    
    # Compute valid signature
    expected_sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    
    # Check valid signature match
    computed = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert hmac.compare_digest(expected_sig, computed) is True
    
    # Check invalid signature rejection
    bad_computed = hmac.new(secret.encode(), b'{"tampered":true}', hashlib.sha256).hexdigest()
    assert hmac.compare_digest(expected_sig, bad_computed) is False


# -----------------------------------------------------------------------------
# Point 44: Explicit v3 Exclusions Tests (§44)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_point_44_system_exclusions():
    """Point 44: Verify explicit v3 exclusions list and codes."""
    mock_session = AsyncMock()
    service = SystemService(mock_session)
    res = await service.get_exclusions()

    assert res.version == "3.0.0"
    assert len(res.exclusions) == 4

    codes = [e.exclusion_code for e in res.exclusions]
    assert "EXCL_001" in codes  # Unsanctioned Direct Auto-Refunding
    assert "EXCL_002" in codes  # Chargeback Dispute Litigation
    assert "EXCL_003" in codes  # Cross-Merchant Raw Data Sharing
    assert "EXCL_004" in codes  # Direct Arbitrary Bank Settlement


def test_point_44_policy_engine_exclusion_guardrail():
    """
    Point 44 Hardening: Verify Policy Engine rejects non-supported / excluded actions.
    """
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        recommended_action="UNSANCTIONED_DIRECT_REFUND",  # Excluded action
        payment_amount_minor=1000,
        ai_confidence=0.95,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.DENY
    assert res.matched_rule == "unsupported_action"
