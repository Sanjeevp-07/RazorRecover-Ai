from typing import Tuple, Optional
from pydantic import BaseModel
from app.models.failure_taxonomy import FailureClass

FAILURE_CLASS_ADJUSTMENTS = {
    FailureClass.INSUFFICIENT_FUNDS: 0.15,
    FailureClass.OTP_3DS_ABANDONED: 0.20,
    FailureClass.GATEWAY_BANK_TIMEOUT: 0.10,
    FailureClass.VPA_INVALID: 0.05,
    FailureClass.EXPIRED_OR_INVALID_INSTRUMENT: -0.10,
    FailureClass.ISSUER_RISK_DECLINE: -0.15,
    FailureClass.UNKNOWN: 0.0,
}

class BaselineScoringResult(BaseModel):
    baseline_probability: float
    is_in_gray_zone: bool
    recommended_action: str
    reason: str

class BaselineScorer:
    """
    Deterministic Baseline Recovery Scorer (§32).
    Computes heuristic baseline probability before/without calling the LLM.
    """

    @staticmethod
    def calculate_baseline(
        customer_history_score: float = 0.5,
        retry_count: int = 0,
        velocity_flag: bool = False,
        failure_class: FailureClass = FailureClass.UNKNOWN,
        gray_zone_lower: float = 0.35,
        gray_zone_upper: float = 0.65
    ) -> BaselineScoringResult:
        # Failure class adjustment
        adj = FAILURE_CLASS_ADJUSTMENTS.get(failure_class, 0.0)

        # Baseline probability computation (§32)
        raw_prob = (
            0.5
            + 0.3 * customer_history_score
            - 0.1 * min(retry_count, 3)
            - 0.2 * (1.0 if velocity_flag else 0.0)
            + adj
        )

        # Clip between 0.0 and 1.0
        prob = max(0.0, min(1.0, round(raw_prob, 3)))
        in_gray_zone = gray_zone_lower <= prob <= gray_zone_upper

        if failure_class == FailureClass.OTP_3DS_ABANDONED:
            recommended_action = "CREATE_RESUME_SESSION"
            reason = f"Mid-funnel dropoff detected. Preserving checkout context with baseline recovery probability {prob}."
        elif prob >= 0.5:
            recommended_action = "CREATE_PAYMENT_LINK"
            reason = f"High baseline recovery score ({prob}) based on customer history ({customer_history_score}) and failure category."
        else:
            recommended_action = "NO_ACTION"
            reason = f"Low recovery probability ({prob}) due to risk/decline factors."

        return BaselineScoringResult(
            baseline_probability=prob,
            is_in_gray_zone=in_gray_zone,
            recommended_action=recommended_action,
            reason=reason
        )
