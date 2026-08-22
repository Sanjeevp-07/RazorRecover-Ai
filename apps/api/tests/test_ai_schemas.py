import uuid
import pytest
from pydantic import ValidationError
from app.ai.schemas import RecoveryRecommendation, RecommendedAction

def test_valid_ai_recovery_recommendation():
    case_id = uuid.uuid4()
    rec = RecoveryRecommendation(
        schema_version="1.0",
        case_id=case_id,
        recovery_probability=0.85,
        recommended_action=RecommendedAction.CREATE_PAYMENT_LINK,
        confidence=0.92,
        requires_human=False,
        reason="High customer history score and low retry velocity.",
        risk_signals=["first_retry_attempt"]
    )

    assert rec.schema_version == "1.0"
    assert rec.case_id == case_id
    assert rec.recovery_probability == 0.85
    assert rec.recommended_action == RecommendedAction.CREATE_PAYMENT_LINK
    assert rec.requires_human is False

def test_invalid_ai_recommendation_probability_out_of_bounds():
    with pytest.raises(ValidationError):
        RecoveryRecommendation(
            schema_version="1.0",
            case_id=uuid.uuid4(),
            recovery_probability=1.5,  # Invalid: > 1.0
            recommended_action=RecommendedAction.CREATE_PAYMENT_LINK,
            confidence=0.9,
            requires_human=False,
            reason="Invalid probability test",
            risk_signals=[]
        )

def test_invalid_ai_recommendation_extra_field_forbidden():
    with pytest.raises(ValidationError):
        RecoveryRecommendation(
            schema_version="1.0",
            case_id=uuid.uuid4(),
            recovery_probability=0.8,
            recommended_action=RecommendedAction.CREATE_PAYMENT_LINK,
            confidence=0.9,
            requires_human=False,
            reason="Extra field test",
            risk_signals=[],
            unallowed_extra_field="hacker"  # Invalid: extra="forbid"
        )
