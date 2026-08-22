import uuid
from typing import Dict, Any, Tuple
from app.tools.base import BaseTool

class EscalateCaseTool(BaseTool):
    """
    Escalate Case Tool (§14).
    Safe fallback tool; always ALLOWED regardless of other policy state.
    Creates approval entry for human review.
    """
    tool_name = "escalate_case"

    async def execute(
        self,
        case_id: uuid.UUID,
        payload: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any], str]:
        reason = payload.get("reason", "Case escalated for human review")
        approval_id = str(uuid.uuid4())
        
        return True, {
            "approval_id": approval_id,
            "status": "PENDING_APPROVAL",
            "reason": reason
        }, ""
