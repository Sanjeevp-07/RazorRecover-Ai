import uuid
import time
import json
import asyncio
from typing import Dict, Any, Tuple, Optional
import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.ai.base import RecoveryReasoner
from app.ai.schemas import RecoveryRecommendation, RecommendedAction

SYSTEM_PROMPT = """You are the AI Revenue Recovery Agent for RazorRecover AI.
Your sole role is to evaluate failed payment cases, analyze payment context and risk signals, and produce a structured recommendation for payment recovery.

Rules:
1. Never claim a payment is recovered.
2. Fail closed: If confidence is low (< 0.7) or risk signals are high, set requires_human: true.
3. Keep reason under 400 characters.
4. Strictly output valid JSON matching schema_version 1.0."""

class OpenAIReasoner(RecoveryReasoner):
    """
    OpenAI Implementation of RecoveryReasoner (§11 & §12).
    Uses temperature 0, strict JSON Schema outputs, 15s timeout, and fail-closed routing.
    Supports custom base_url for free LLM providers (Groq, OpenRouter, Ollama).
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_id: Optional[str] = None
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY or "mock-key-for-dev-testing"
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.model_id = model_id or settings.AI_MODEL_PRIMARY

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = AsyncOpenAI(**client_kwargs)

    async def analyze(
        self,
        case_id: uuid.UUID,
        context: Dict[str, Any]
    ) -> Tuple[Optional[RecoveryRecommendation], bool, str, int]:
        """
        Analyze recovery case context using OpenAI / LLM provider.
        Enforces 15s per-call timeout and 2 retries (§11.3).
        Fails closed on error or validation failure (§12.2).
        """
        start_time = time.time()
        user_content = json.dumps(context, indent=2)

        # Retry loop: 2 retries with exponential backoff (1s, 3s) (§11.3)
        retries = 2
        backoffs = [1, 3]
        raw_output_text = ""

        for attempt in range(retries + 1):
            try:
                # Enforce 15 seconds per call timeout (§11.3)
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model_id,
                        temperature=0,  # Deterministic reasoning (§11.3)
                        max_tokens=600,
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"Case ID: {case_id}\nContext:\n{user_content}"}
                        ]
                    ),
                    timeout=15.0
                )
                
                raw_output_text = response.choices[0].message.content or ""
                latency_ms = int((time.time() - start_time) * 1000)

                # Validate output schema server-side (§12.2)
                try:
                    parsed_json = json.loads(raw_output_text)
                    if "case_id" not in parsed_json:
                        parsed_json["case_id"] = str(case_id)
                    
                    recommendation = RecoveryRecommendation.model_validate(parsed_json)
                    return recommendation, True, raw_output_text, latency_ms
                except Exception as val_err:
                    # Schema validation failed -> fail closed (§12.2)
                    fallback = self._build_fail_closed_recommendation(
                        case_id,
                        f"AI Schema validation failure: {str(val_err)[:100]}"
                    )
                    return fallback, False, raw_output_text, latency_ms

            except Exception as exc:
                if attempt < retries:
                    await asyncio.sleep(backoffs[attempt])
                else:
                    latency_ms = int((time.time() - start_time) * 1000)
                    fallback = self._build_fail_closed_recommendation(
                        case_id,
                        f"AI service unavailable or timed out: {str(exc)[:100]}"
                    )
                    return fallback, False, str(exc), latency_ms

        latency_ms = int((time.time() - start_time) * 1000)
        fallback = self._build_fail_closed_recommendation(case_id, "AI service call exhausted retries")
        return fallback, False, raw_output_text, latency_ms

    def _build_fail_closed_recommendation(self, case_id: uuid.UUID, reason_msg: str) -> RecoveryRecommendation:
        """
        Fail closed helper (§11.3 & §12.2):
        Routes unserviceable or invalid LLM calls to HUMAN_APPROVAL safely.
        """
        return RecoveryRecommendation(
            schema_version="1.0",
            case_id=case_id,
            recovery_probability=0.0,
            recommended_action=RecommendedAction.ESCALATE_CASE,
            confidence=0.0,
            requires_human=True,
            reason=reason_msg[:390],
            risk_signals=["ai_unavailable"]
        )
