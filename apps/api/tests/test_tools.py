import uuid
import pytest
from unittest.mock import AsyncMock
from app.tools.base import BaseTool
from app.tools.payment_link_tool import CreatePaymentLinkTool
from app.tools.notification_tool import SendNotificationTool
from app.tools.escalate_tool import EscalateCaseTool
from app.integrations.razorpay.client import RazorpayClient

def test_tool_idempotency_key_generation():
    case_id = uuid.uuid4()
    key_primary = BaseTool.generate_idempotency_key(case_id, "create_payment_link", "primary")
    key_retry1 = BaseTool.generate_idempotency_key(case_id, "create_payment_link", "retry-1")

    assert len(key_primary) == 64  # SHA256 hex string length
    assert key_primary != key_retry1
    assert key_primary == BaseTool.generate_idempotency_key(case_id, "create_payment_link", "primary")

@pytest.mark.asyncio
async def test_create_payment_link_tool_execution():
    case_id = uuid.uuid4()
    mock_r_client = RazorpayClient()
    mock_r_client.create_payment_link = AsyncMock(return_value={
        "id": "plink_12345",
        "short_url": "https://rzp.io/i/test",
        "status": "created"
    })

    tool = CreatePaymentLinkTool(mock_r_client)
    success, output, err = await tool.execute(case_id, {"amount_minor": 1000, "currency": "INR"})

    assert success is True
    assert output["link_id"] == "plink_12345"
    assert output["short_url"] == "https://rzp.io/i/test"
    assert err == ""

@pytest.mark.asyncio
async def test_send_notification_tool_approved_template():
    case_id = uuid.uuid4()
    tool = SendNotificationTool()
    
    success, output, err = await tool.execute(case_id, {"template": "payment_failed_reminder", "channel": "email"})
    assert success is True
    assert output["template"] == "payment_failed_reminder"

@pytest.mark.asyncio
async def test_send_notification_tool_unapproved_template_fails():
    case_id = uuid.uuid4()
    tool = SendNotificationTool()
    
    success, output, err = await tool.execute(case_id, {"template": "free_text_unapproved_template"})
    assert success is False
    assert err == "invalid_template"

@pytest.mark.asyncio
async def test_escalate_case_tool():
    case_id = uuid.uuid4()
    tool = EscalateCaseTool()
    
    success, output, err = await tool.execute(case_id, {"reason": "High risk score"})
    assert success is True
    assert output["status"] == "PENDING_APPROVAL"
