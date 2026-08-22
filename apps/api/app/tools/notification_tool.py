import uuid
from typing import Dict, Any, Tuple
from app.tools.base import BaseTool

APPROVED_TEMPLATES = {"payment_failed_reminder", "payment_link_created", "recovery_success"}

class SendNotificationTool(BaseTool):
    """
    Send Notification Tool (§14).
    Guardrail: template must be one of a fixed enum; no free text passed to provider.
    """
    tool_name = "send_notification"

    async def execute(
        self,
        case_id: uuid.UUID,
        payload: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any], str]:
        template = payload.get("template", "payment_failed_reminder")
        channel = payload.get("channel", "email")

        if template not in APPROVED_TEMPLATES:
            return False, {"error": f"Template '{template}' is not in approved list"}, "invalid_template"

        # Simulating notification dispatch stub
        notification_id = f"notif_{uuid.uuid4()}"
        return True, {
            "notification_id": notification_id,
            "channel": channel,
            "template": template,
            "status": "sent"
        }, ""
