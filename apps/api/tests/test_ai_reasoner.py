import uuid
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.ai.openai_provider import OpenAIReasoner
from app.ai.schemas import RecommendedAction

@pytest.mark.asyncio
async def test_openai_reasoner_valid_recommendation():
    case_id = uuid.uuid4()
    mock_payload = {
        "schema_version": "1.0",
        "case_id": str(case_id),
        "recovery_probability": 0.88,
        "recommended_action": "CREATE_PAYMENT_LINK",
        "confidence": 0.95,
        "requires_human": False,
        "reason": "Customer history is strong and payment failure is temporary.",
        "risk_signals": ["low_retry_count"]
    }

    reasoner = OpenAIReasoner(api_key="mock-key")
    
    mock_message = MagicMock()
    mock_message.content = json.dumps(mock_payload)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch.object(reasoner.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        rec, is_valid, raw_str, latency_ms = await reasoner.analyze(case_id, {"payment_amount": 250000})

        assert is_valid is True
        assert rec is not None
        assert rec.case_id == case_id
        assert rec.recommended_action == RecommendedAction.CREATE_PAYMENT_LINK
        assert rec.requires_human is False

@pytest.mark.asyncio
async def test_openai_reasoner_malformed_json_fails_closed():
    case_id = uuid.uuid4()
    reasoner = OpenAIReasoner(api_key="mock-key")

    mock_message = MagicMock()
    mock_message.content = "INVALID_NON_JSON_RESPONSE"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch.object(reasoner.client.chat.completions, "create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        rec, is_valid, raw_str, latency_ms = await reasoner.analyze(case_id, {"payment_amount": 250000})

        # Must fail closed (§12.2)
        assert is_valid is False
        assert rec is not None
        assert rec.requires_human is True
        assert rec.recommended_action == RecommendedAction.ESCALATE_CASE

@pytest.mark.asyncio
async def test_openai_reasoner_timeout_fails_closed():
    case_id = uuid.uuid4()
    reasoner = OpenAIReasoner(api_key="mock-key")

    with patch.object(reasoner.client.chat.completions, "create", side_effect=TimeoutError("API Call Timed Out")):
        rec, is_valid, raw_str, latency_ms = await reasoner.analyze(case_id, {"payment_amount": 250000})

        # Must fail closed on timeout (§11.3)
        assert is_valid is False
        assert rec is not None
        assert rec.requires_human is True
        assert rec.recommended_action == RecommendedAction.ESCALATE_CASE
