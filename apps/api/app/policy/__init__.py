"""
Policy & Guardrail Engine Package.
Deterministic authorization pure functions (context -> decision) (§13).
No I/O.
"""
from app.policy.engine import evaluate_policy, PolicyEvaluationContext, PolicyDecisionResult

__all__ = [
    "evaluate_policy",
    "PolicyEvaluationContext",
    "PolicyDecisionResult"
]
