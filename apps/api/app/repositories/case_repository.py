import uuid
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.repositories.base import BaseRepository
from app.models.recovery_case import RecoveryCase, RecoveryCaseStatus
from app.models.audit_log import AuditLog
from app.models.ai_decision import AIDecision
from app.models.policy_decision import PolicyDecision
from app.models.approval import Approval, ApprovalStatus
from app.models.risk_signal import RiskSignal
from app.models.action_execution import ActionExecution

class CaseRepository(BaseRepository[RecoveryCase]):
    """Repository for managing recovery_cases and associated lifecycle records."""
    def __init__(self, session: AsyncSession, merchant_id: uuid.UUID):
        super().__init__(RecoveryCase, session, merchant_id)

    async def get_open_case_by_payment_id(self, payment_id: uuid.UUID) -> Optional[RecoveryCase]:
        """Fetch open recovery case for a payment if one exists."""
        stmt = select(RecoveryCase).where(
            RecoveryCase.payment_id == payment_id,
            RecoveryCase.merchant_id == self.merchant_id,
            RecoveryCase.status.in_([
                RecoveryCaseStatus.OPEN,
                RecoveryCaseStatus.ANALYZING,
                RecoveryCaseStatus.PENDING_APPROVAL,
                RecoveryCaseStatus.EXECUTING
            ])
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_cases_paginated(
        self,
        status_filter: Optional[RecoveryCaseStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[RecoveryCase], int]:
        """List recovery cases with pagination and status filtering."""
        query = select(RecoveryCase).where(RecoveryCase.merchant_id == self.merchant_id)
        count_query = select(func.count(RecoveryCase.id)).where(RecoveryCase.merchant_id == self.merchant_id)

        if status_filter:
            query = query.where(RecoveryCase.status == status_filter)
            count_query = count_query.where(RecoveryCase.status == status_filter)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(RecoveryCase.created_at.desc()).offset(offset).limit(limit)
        items_res = await self.session.execute(query)
        items = list(items_res.scalars().all())

        return items, total

    async def get_latest_ai_decision(self, case_id: uuid.UUID) -> Optional[AIDecision]:
        """Fetch latest AI decision for case."""
        stmt = select(AIDecision).where(AIDecision.case_id == case_id).order_by(AIDecision.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_policy_decision(self, case_id: uuid.UUID) -> Optional[PolicyDecision]:
        """Fetch latest policy decision for case."""
        stmt = select(PolicyDecision).where(PolicyDecision.case_id == case_id).order_by(PolicyDecision.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_approval(self, case_id: uuid.UUID) -> Optional[Approval]:
        """Fetch pending approval for case."""
        stmt = select(Approval).where(
            Approval.case_id == case_id,
            Approval.status == ApprovalStatus.PENDING
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_risk_signal(self, case_id: uuid.UUID) -> Optional[RiskSignal]:
        """Fetch latest computed risk signal for case."""
        stmt = select(RiskSignal).where(RiskSignal.case_id == case_id).order_by(RiskSignal.computed_at.desc())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_timeline_by_correlation_id(self, correlation_id: uuid.UUID) -> List[AuditLog]:
        """Fetch ordered audit logs for correlation_id timeline (§9.2)."""
        stmt = select(AuditLog).where(
            AuditLog.correlation_id == correlation_id,
            AuditLog.merchant_id == self.merchant_id
        ).order_by(AuditLog.created_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_audit_log(self, correlation_id: uuid.UUID, event_type: str, payload: dict) -> AuditLog:
        """Add audit log entry in same transaction as state change (§2)."""
        log = AuditLog(
            merchant_id=self.merchant_id,
            correlation_id=correlation_id,
            event_type=event_type,
            payload=payload
        )
        self.session.add(log)
        await self.session.flush()
        return log
