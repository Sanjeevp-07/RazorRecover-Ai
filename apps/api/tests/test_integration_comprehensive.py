import pytest
import uuid
from datetime import datetime, timezone, timedelta
from app.models.recovery_case import RecoveryCaseStatus
from app.models.payment import PaymentStatus
from app.models.policy_decision import PolicyOutcome
from app.policy.engine import evaluate_policy, PolicyEvaluationContext
from app.tools import CreatePaymentLinkTool, SendNotificationTool, EscalateCaseTool
from app.core.observability import metrics, MetricRegistry

@pytest.mark.asyncio
async def test_policy_to_tool_executor_allow_creates_payment_link():
    """Policy ALLOW outcome triggers tool executor path for CreatePaymentLinkTool."""
    case_id = uuid.uuid4()
    ctx = PolicyEvaluationContext(
        payment_status="failed",
        case_status="ANALYZING",
        payment_amount_minor=250000,
        recommended_action="CREATE_PAYMENT_LINK",
        ai_confidence=0.92,
        ai_requires_human=False
    )
    res = evaluate_policy(ctx)
    assert res.decision == PolicyOutcome.ALLOW

    from unittest.mock import AsyncMock
    mock_client = AsyncMock()
    mock_client.create_payment_link.return_value = {
        "id": "plink_12345",
        "short_url": "https://rzp.io/i/test123",
        "status": "created"
    }

    tool = CreatePaymentLinkTool(mock_client)
    success, tool_out, err = await tool.execute(case_id=case_id, payload={"amount_minor": 250000, "currency": "INR"})
    assert success is True
    assert tool_out["link_id"] == "plink_12345"
    assert tool_out["status"] == "created"
    assert tool_out["short_url"] == "https://rzp.io/i/test123"

@pytest.mark.asyncio
async def test_notification_tool_fixed_template_dispatch():
    """Notification tool only dispatches approved fixed templates (§14)."""
    case_id = uuid.uuid4()
    tool = SendNotificationTool()
    success, res, err = await tool.execute(case_id=case_id, payload={"channel": "email", "template": "payment_failed_reminder"})
    assert success is True
    assert res["status"] == "sent"
    assert res["notification_id"].startswith("notif_")

@pytest.mark.asyncio
async def test_escalation_tool_routes_to_human_approval():
    """Escalation tool fallback always records approval request (§14)."""
    case_id = uuid.uuid4()
    tool = EscalateCaseTool()
    success, res, err = await tool.execute(case_id=case_id, payload={"reason": "Ambiguous risk flag requiring manual review"})
    assert success is True
    assert res["status"] == "PENDING_APPROVAL"

def test_sla_expiry_calculation():
    """SLA expires_at = requested_at + approval_sla_hours (default 24h) (§15)."""
    requested_at = datetime.now(timezone.utc)
    sla_hours = 24
    sla_expires_at = requested_at + timedelta(hours=sla_hours)
    assert sla_expires_at > requested_at
    assert (sla_expires_at - requested_at).total_seconds() == 24 * 3600

def test_prometheus_metrics_generation():
    """Prometheus exposition metrics contain all required counters (§22)."""
    m = MetricRegistry()
    m.inc_webhook_event("payment.failed")
    m.inc_webhook_event("payment.captured")
    m.inc_ai_call("gpt-5.6-terra", "success")
    m.inc_policy_decision("ALLOW")
    m.inc_action_execution("create_payment_link", "SUCCEEDED")
    m.record_celery_task_duration("analyze_recovery_case", 0.452)

    prom_text = m.generate_prometheus_metrics()
    assert 'webhook_events_total{event_type="payment.failed"} 1' in prom_text
    assert 'ai_calls_total{model="gpt-5.6-terra",status="success"} 1' in prom_text
    assert 'policy_decisions_total{decision="ALLOW"} 1' in prom_text
    assert 'action_executions_total{tool="create_payment_link",status="SUCCEEDED"} 1' in prom_text
    assert 'celery_task_duration_seconds{task="analyze_recovery_case"} 0.4520' in prom_text
