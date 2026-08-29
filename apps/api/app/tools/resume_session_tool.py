import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple
from app.tools.base import BaseTool

class CreateResumeSessionTool(BaseTool):
    """
    Tool: Create Merchant-Hosted Resume Checkout Session (§31).
    Used specifically for dropped-off sessions (e.g. OTP_3DS_ABANDONED)
    to preserve customer cart context, order details, and branding.
    """
    tool_name = "CREATE_RESUME_SESSION"

    def __init__(self, base_checkout_url: str = "https://checkout.merchant.com/resume"):
        self.base_checkout_url = base_checkout_url

    async def execute(self, case_id: uuid.UUID, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        Generate a secure context-preserving resume checkout session URL.
        Returns (success, output_payload, error_category).
        """
        try:
            session_token = uuid.uuid4().hex
            expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
            resume_url = f"{self.base_checkout_url}?token={session_token}&case_id={case_id}"

            output = {
                "session_token": session_token,
                "resume_url": resume_url,
                "expires_at": expires_at,
                "type": "RESUME_CHECKOUT_SESSION",
                "status": "active"
            }
            return True, output, ""

        except Exception as exc:
            return False, {}, f"RESUME_SESSION_ERROR: {str(exc)}"
