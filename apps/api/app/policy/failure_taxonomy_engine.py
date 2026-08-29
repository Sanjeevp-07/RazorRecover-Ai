from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.models.failure_taxonomy import FailureClass

class TaxonomyClassificationResult(BaseModel):
    failure_class: FailureClass
    matched_signal: str
    suggested_treatment: str
    default_channel: str
    default_delay_minutes: int
    default_tone: str
    native_retry_grace_minutes: int
    is_hard_decline: bool

class FailureTaxonomyEngine:
    """
    Deterministic Failure Taxonomy Engine (§30).
    Classifies Razorpay error payload signals into standardized failure classes.
    Pure function — zero LLM calls, zero I/O.
    """

    @classmethod
    def classify_failure(
        cls,
        error_code: Optional[str] = None,
        error_description: Optional[str] = None,
        error_reason: Optional[str] = None,
        error_source: Optional[str] = None,
        error_step: Optional[str] = None,
        method: Optional[str] = None
    ) -> TaxonomyClassificationResult:
        code = (error_code or "").lower()
        desc = (error_description or "").lower()
        reason = (error_reason or "").lower()
        source = (error_source or "").lower()
        step = (error_step or "").lower()
        pay_method = (method or "").lower()

        combined_text = f"{code} {desc} {reason}"

        # 1. OTP / 3DS Abandoned (§30)
        if (
            step == "payment_authentication" 
            or "otp" in combined_text 
            or "3ds" in combined_text 
            or "authentication" in combined_text
            or "timed out waiting for user" in combined_text
            or "abandoned" in combined_text
        ):
            return TaxonomyClassificationResult(
                failure_class=FailureClass.OTP_3DS_ABANDONED,
                matched_signal="authentication_or_otp_dropoff",
                suggested_treatment="Issue resume-checkout link with cart context; customer was mid-flow.",
                default_channel="WHATSAPP",
                default_delay_minutes=5,
                default_tone="urgent",
                native_retry_grace_minutes=0,
                is_hard_decline=False
            )

        # 2. Insufficient Funds (§30)
        if (
            "insufficient" in combined_text 
            or "low_balance" in combined_text 
            or "not enough balance" in combined_text
            or "limit exceeded" in combined_text
        ):
            return TaxonomyClassificationResult(
                failure_class=FailureClass.INSUFFICIENT_FUNDS,
                matched_signal="balance_or_funds_limit",
                suggested_treatment="Delay outreach before retrying; empathetic messaging with no immediate alternate-method force.",
                default_channel="WHATSAPP",
                default_delay_minutes=240,
                default_tone="empathetic",
                native_retry_grace_minutes=0,
                is_hard_decline=False
            )

        # 3. Invalid VPA / UPI handle (§30)
        if pay_method == "upi" and (
            "vpa" in combined_text 
            or "invalid_handle" in combined_text 
            or "handle does not exist" in combined_text
            or "beneficiary" in combined_text
        ):
            return TaxonomyClassificationResult(
                failure_class=FailureClass.VPA_INVALID,
                matched_signal="upi_vpa_validation_error",
                suggested_treatment="Prompt for corrected UPI VPA ID; avoid blind auto-retry.",
                default_channel="WHATSAPP",
                default_delay_minutes=0,
                default_tone="action-oriented",
                native_retry_grace_minutes=0,
                is_hard_decline=False
            )

        # 4. Expired or Invalid Instrument (§30)
        if (
            "expired" in combined_text 
            or "invalid_card" in combined_text 
            or "invalid_cvv" in combined_text
            or "card_number_invalid" in combined_text
        ):
            return TaxonomyClassificationResult(
                failure_class=FailureClass.EXPIRED_OR_INVALID_INSTRUMENT,
                matched_signal="expired_or_invalid_instrument",
                suggested_treatment="Prompt for updated payment instrument / valid card credentials.",
                default_channel="WHATSAPP",
                default_delay_minutes=0,
                default_tone="action-oriented",
                native_retry_grace_minutes=0,
                is_hard_decline=True
            )

        # 5. Gateway / Bank Timeout / Network Error (Soft technical decline) (§30)
        if (
            source in ("gateway", "network", "bank", "system") and (
                "timeout" in combined_text
                or "timed out" in combined_text
                or "timed_out" in combined_text
                or "system_error" in combined_text
                or "network_error" in combined_text
                or "technical_error" in combined_text
                or "service_unavailable" in combined_text
                or "gateway" in combined_text
            )
        ) or (
            "timed out" in combined_text or "timeout" in combined_text or "gateway_error" in combined_text
        ):
            return TaxonomyClassificationResult(
                failure_class=FailureClass.GATEWAY_BANK_TIMEOUT,
                matched_signal="gateway_or_network_timeout",
                suggested_treatment="Apply native-retry grace window to allow Razorpay Smart Retry first; then send retry link if unresolved.",
                default_channel="WHATSAPP",
                default_delay_minutes=15,
                default_tone="supportive",
                native_retry_grace_minutes=15,
                is_hard_decline=False
            )

        # 6. Issuer Risk Decline (Hard decline) (§30)
        if (
            source in ("bank", "issuer") or
            "do_not_honor" in combined_text or
            "declined" in combined_text or
            "blocked" in combined_text or
            "fraud" in combined_text or
            "restricted" in combined_text or
            "not permitted" in combined_text
        ):
            return TaxonomyClassificationResult(
                failure_class=FailureClass.ISSUER_RISK_DECLINE,
                matched_signal="bank_issuer_risk_decline",
                suggested_treatment="Suggest an alternate payment method (UPI / NetBanking) rather than retrying same instrument.",
                default_channel="WHATSAPP",
                default_delay_minutes=0,
                default_tone="direct",
                native_retry_grace_minutes=0,
                is_hard_decline=True
            )

        # 7. Fallback / UNKNOWN (§30)
        return TaxonomyClassificationResult(
            failure_class=FailureClass.UNKNOWN,
            matched_signal="unmapped_combination",
            suggested_treatment="Falls through to AI reasoning with requires_human bias; log for taxonomy review.",
            default_channel="WHATSAPP",
            default_delay_minutes=0,
            default_tone="neutral",
            native_retry_grace_minutes=0,
            is_hard_decline=False
        )
