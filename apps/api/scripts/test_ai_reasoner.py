import sys
from pathlib import Path

# Ensure app package is in python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid
import asyncio
import json
from app.ai.openai_provider import OpenAIReasoner
from app.core.config import settings

async def main():
    print("\n--- RAZORRECOVER AI REASONER (SECTION 11 & 12 TEST) ---")
    print(f"Primary Model ID: {settings.AI_MODEL_PRIMARY}")
    print(f"Base URL: {settings.OPENAI_BASE_URL or 'Default (OpenAI Direct)'}")
    print("------------------------------------------------------")

    case_id = uuid.uuid4()
    context = {
        "payment": {
          "amount_minor": 250000,
          "currency": "INR",
          "failure_reason": "insufficient_funds",
          "method": "card"
        },
        "customer_history": {
          "past_payments_count": 12,
          "successful_recoveries": 10,
          "customer_history_score": 0.85
        },
        "risk_signals": {
          "retry_count": 1,
          "velocity_flag": False
        }
    }

    print(f"\nAnalyzing Case ID: {case_id}...")
    print(f"Input Context:\n{json.dumps(context, indent=2)}")

    reasoner = OpenAIReasoner()
    rec, is_valid, raw_output, latency_ms = await reasoner.analyze(case_id, context)

    print("\n--- ANALYSIS RESULT ---")
    print(f"Is Schema Valid: {is_valid}")
    print(f"Latency: {latency_ms} ms")
    if rec:
        print(f"Schema Version: {rec.schema_version}")
        print(f"Recommended Action: {rec.recommended_action.value}")
        print(f"Recovery Probability: {rec.recovery_probability}")
        print(f"Confidence Score: {rec.confidence}")
        print(f"Requires Human Approval: {rec.requires_human}")
        print(f"Reason: {rec.reason}")
        print(f"Risk Signals: {rec.risk_signals}")
    print("-----------------------\n")

if __name__ == "__main__":
    asyncio.run(main())
