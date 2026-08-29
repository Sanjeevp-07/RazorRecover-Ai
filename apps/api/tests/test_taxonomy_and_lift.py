import pytest
import uuid
from app.models.failure_taxonomy import FailureClass
from app.models.experiment_assignment import CohortType, ExperimentAssignment
from app.models.action_execution import ActionExecutionStatus
from app.policy.failure_taxonomy_engine import FailureTaxonomyEngine
from app.schemas.lift import CausalLiftResponse

def test_failure_taxonomy_otp_abandoned():
    res = FailureTaxonomyEngine.classify_failure(
        error_code="BAD_REQUEST_ERROR",
        error_description="Customer dropped off at OTP screen",
        error_step="payment_authentication"
    )
    assert res.failure_class == FailureClass.OTP_3DS_ABANDONED
    assert res.default_tone == "urgent"
    assert res.native_retry_grace_minutes == 0
    assert not res.is_hard_decline

def test_failure_taxonomy_insufficient_funds():
    res = FailureTaxonomyEngine.classify_failure(
        error_code="BAD_REQUEST_ERROR",
        error_description="Transaction failed due to insufficient funds in account",
        error_reason="insufficient_funds"
    )
    assert res.failure_class == FailureClass.INSUFFICIENT_FUNDS
    assert res.default_delay_minutes == 240
    assert res.default_tone == "empathetic"
    assert not res.is_hard_decline

def test_failure_taxonomy_invalid_vpa():
    res = FailureTaxonomyEngine.classify_failure(
        error_code="BAD_REQUEST_ERROR",
        error_description="Invalid VPA address entered",
        method="upi"
    )
    assert res.failure_class == FailureClass.VPA_INVALID
    assert res.default_tone == "action-oriented"

def test_failure_taxonomy_expired_instrument():
    res = FailureTaxonomyEngine.classify_failure(
        error_code="BAD_REQUEST_ERROR",
        error_description="The card provided has expired",
        error_reason="expired_card"
    )
    assert res.failure_class == FailureClass.EXPIRED_OR_INVALID_INSTRUMENT
    assert res.is_hard_decline is True

def test_failure_taxonomy_gateway_timeout_with_grace():
    res = FailureTaxonomyEngine.classify_failure(
        error_code="GATEWAY_ERROR",
        error_description="Bank system timed out waiting for response",
        error_source="gateway"
    )
    assert res.failure_class == FailureClass.GATEWAY_BANK_TIMEOUT
    assert res.native_retry_grace_minutes == 15
    assert not res.is_hard_decline

def test_failure_taxonomy_issuer_risk_decline():
    res = FailureTaxonomyEngine.classify_failure(
        error_code="ISSUER_ERROR",
        error_description="Card issuer declined transaction do_not_honor",
        error_source="bank"
    )
    assert res.failure_class == FailureClass.ISSUER_RISK_DECLINE
    assert res.native_retry_grace_minutes == 0
    assert res.is_hard_decline is True

def test_failure_taxonomy_unknown_fallback():
    res = FailureTaxonomyEngine.classify_failure(
        error_code="CUSTOM_UNKNOWN_CODE",
        error_description="An unspecified condition occurred"
    )
    assert res.failure_class == FailureClass.UNKNOWN
    assert res.native_retry_grace_minutes == 0

def test_causal_lift_schema_validation():
    payload = {
        "treatment_cases_count": 100,
        "treatment_recovered_count": 45,
        "recovered_rate_treatment": 0.45,
        "control_cases_count": 10,
        "control_recovered_count": 2,
        "recovered_rate_control": 0.20,
        "incremental_recovery_rate": 0.25,
        "incremental_recovered_revenue_minor": 1250000,
        "current_sample_size": 10,
        "sample_size_sufficient": False,
        "message": "Holdout sample accumulating (10/30 cases)."
    }
    schema = CausalLiftResponse(**payload)
    assert schema.incremental_recovery_rate == 0.25
    assert schema.incremental_recovered_revenue_minor == 1250000
    assert schema.sample_size_sufficient is False
