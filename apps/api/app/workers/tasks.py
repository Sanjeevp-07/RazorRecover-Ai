import uuid
from datetime import datetime, timezone
import asyncio
from typing import Dict, Any

from app.workers.celery_app import celery_app
from app.core.db import SyncSessionLocal, AsyncSessionLocal
from app.models.approval import Approval, ApprovalStatus
from app.models.recovery_case import RecoveryCase, RecoveryCaseStatus
from app.services.recovery_orchestrator import RecoveryOrchestrator

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_webhook_event(self, webhook_event_id: str):
    """
    Celery Task: Ingestion processing for webhook event (§16.2).
    Queue: webhooks
    """
    pass

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def analyze_recovery_case(self, case_id: str, merchant_id: str):
    """
    Celery Task: Asynchronous recovery case analysis pipeline (§16.2).
    Queue: analysis
    Retries: max 3 attempts with exponential backoff (10s, 60s, 300s) (§16.3).
    """
    try:
        c_uuid = uuid.UUID(case_id)
        m_uuid = uuid.UUID(merchant_id)
        
        async def run_pipeline():
            async with AsyncSessionLocal() as session:
                orchestrator = RecoveryOrchestrator(session, m_uuid)
                return await orchestrator.execute_recovery_pipeline(c_uuid)

        return asyncio.run(run_pipeline())

    except Exception as exc:
        backoffs = [10, 60, 300]
        retry_num = min(self.request.retries, len(backoffs) - 1)
        countdown = backoffs[retry_num]
        raise self.retry(exc=exc, countdown=countdown)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def send_notification(self, case_id: str, channel: str, template: str):
    """
    Celery Task: Asynchronous notification delivery (§16.2).
    Queue: notifications
    """
    pass

@celery_app.task
def expire_overdue_approvals():
    """
    Celery Beat Task: Expire overdue approvals past SLA every 15 minutes (§15 & §16.2).
    Queue: scheduled
    Sets any approval past SLA to EXPIRED and case to EXPIRED — never auto-approves.
    Uses sync driver (psycopg2) per §3 worker rule.
    """
    now = datetime.now(timezone.utc)
    with SyncSessionLocal() as session:
        overdue_approvals = session.query(Approval).filter(
            Approval.status == ApprovalStatus.PENDING,
            Approval.sla_expires_at < now
        ).all()

        for approval in overdue_approvals:
            approval.status = ApprovalStatus.EXPIRED
            case = session.query(RecoveryCase).filter(
                RecoveryCase.id == approval.case_id
            ).first()
            if case:
                case.status = RecoveryCaseStatus.EXPIRED

        session.commit()
    return len(overdue_approvals)
