import pytest
from app.ai.evaluator import SyntheticEvaluator

def test_synthetic_ai_evaluation_benchmark():
    """Run §20.4 AI Evaluation comparing Baseline vs AI Agent on synthetic dataset."""
    evaluator = SyntheticEvaluator()
    results = evaluator.run_comparison()

    baseline = results["baseline"]
    ai_agent = results["ai_agent"]
    uplift = results["uplift"]

    # 1. Verify Dataset Size
    assert baseline["total_cases"] >= 100
    assert ai_agent["total_cases"] >= 100

    # 2. Assert Zero False Retries for AI Agent (Strict Guardrails)
    assert ai_agent["false_retries"] == 0
    assert ai_agent["false_positive_rate"] == 0.0

    # 3. Assert Positive Recovery Rate Uplift Over Naive Baseline
    assert ai_agent["recovery_rate"] > baseline["recovery_rate"]
    assert uplift["net_recovery_rate_uplift"] > 0
    assert uplift["net_value_uplift_minor"] > 0
    assert uplift["status"] == "AI_AGENT_OUTPERFORMS_BASELINE"
