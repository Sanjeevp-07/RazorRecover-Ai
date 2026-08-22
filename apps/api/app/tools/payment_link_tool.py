import uuid
from typing import Dict, Any, Tuple
from app.tools.base import BaseTool
from app.integrations.razorpay.client import RazorpayClient

class CreatePaymentLinkTool(BaseTool):
    """
    Create Payment Link Tool (§14).
    Guardrail: Policy = ALLOW required; amount must equal payment amount.
    """
    tool_name = "create_payment_link"

    def __init__(self, razorpay_client: RazorpayClient):
        self.client = razorpay_client

    async def execute(
        self,
        case_id: uuid.UUID,
        payload: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any], str]:
        """Execute Razorpay Payment Link creation."""
        amount_minor = payload.get("amount_minor", 0)
        currency = payload.get("currency", "INR")
        description = payload.get("description", f"Payment Link for case {case_id}")
        email = payload.get("customer_email")
        phone = payload.get("customer_phone")

        try:
            res = await self.client.create_payment_link(
                amount_minor=amount_minor,
                currency=currency,
                description=description,
                customer_email=email,
                customer_phone=phone,
                notes={"case_id": str(case_id)}
            )
            return True, {
                "link_id": res.get("id"),
                "short_url": res.get("short_url"),
                "status": res.get("status")
            }, ""
        except Exception as exc:
            return False, {"error": str(exc)}, "provider_timeout"
