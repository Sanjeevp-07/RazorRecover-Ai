import uuid
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.case_repository import CaseRepository
from app.repositories.payment_repository import PaymentRepository
from app.models.recovery_case import RecoveryCase, RecoveryCaseStatus
from app.models.approval import ApprovalStatus
from app.models.payment import PaymentStatus
from app.schemas.case import (
    RecoveryCaseDetailResponse,
    PaymentSummarySchema,
    RiskSignalsSummarySchema,
    AIDecisionSummarySchema,
    PolicyDecisionSummarySchema,
    ApprovalSummarySchema,
    AuditLogTimelineItem,
    RecoveryCaseListItemResponse
)
from app.schemas.dashboard import DashboardSummaryResponse

class RecoveryCaseService:
    """Service layer managing recovery cases, approvals, timeline, and analytics (§9 & §15)."""
    def __init__(self, session: AsyncSession, merchant_id: uuid.UUID):
        self.session = session
        self.merchant_id = merchant_id
        self.case_repo = CaseRepository(session, merchant_id)
        self.payment_repo = PaymentRepository(session, merchant_id)

    async def list_cases(
        self,
        status_filter: Optional[RecoveryCaseStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[RecoveryCaseListItemResponse], int]:
        """List recovery cases with pagination and status filter."""
        offset = (page - 1) * page_size
        cases, total = await self.case_repo.list_cases_paginated(status_filter, limit=page_size, offset=offset)

        items = [
            RecoveryCaseListItemResponse(
                id=c.id,
                merchant_id=c.merchant_id,
                payment_id=c.payment_id,
                status=c.status,
                correlation_id=c.correlation_id,
                created_at=c.created_at,
                updated_at=c.updated_at
            ) for c in cases
        ]
        return items, total

    async def get_case_detail(self, case_id: uuid.UUID) -> RecoveryCaseDetailResponse:
        """Fetch full case detail including payment, risk signals, AI & Policy decisions (§9.2)."""
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recovery case not found")

        payment = await self.payment_repo.get_by_id(case.payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated payment record not found")

        payment_summary = PaymentSummarySchema(
            id=payment.id,
            amount_minor=payment.amount_minor,
            currency=payment.currency,
            status=payment.status.value
        )

        risk = await self.case_repo.get_latest_risk_signal(case_id)
        risk_summary = RiskSignalsSummarySchema(
            retry_count=risk.retry_count,
            customer_history_score=float(risk.customer_history_score),
            velocity_flag=risk.velocity_flag
        ) if risk else None

        ai = await self.case_repo.get_latest_ai_decision(case_id)
        ai_summary = None
        if ai and ai.validated_output:
            out = ai.validated_output
            ai_summary = AIDecisionSummarySchema(
                recommended_action=out.get("recommended_action", "NO_ACTION"),
                recovery_probability=float(out.get("recovery_probability", 0.0)),
                confidence=float(out.get("confidence", 0.0)),
                requires_human=bool(out.get("requires_human", False)),
                reason=out.get("reason", ""),
                schema_version=ai.schema_version
            )

        policy = await self.case_repo.get_latest_policy_decision(case_id)
        policy_summary = PolicyDecisionSummarySchema(
            decision=policy.decision.value,
            matched_rule=policy.matched_rule,
            policy_version=policy.policy_version
        ) if policy else None

        approval = await self.case_repo.get_pending_approval(case_id)
        approval_summary = ApprovalSummarySchema(
            status=approval.status.value,
            sla_expires_at=approval.sla_expires_at
        ) if approval else None

        return RecoveryCaseDetailResponse(
            id=case.id,
            status=case.status,
            payment=payment_summary,
            risk_signals=risk_summary,
            ai_decision=ai_summary,
            policy_decision=policy_summary,
            approval=approval_summary
        )

    async def approve_case(self, case_id: uuid.UUID, user_id: uuid.UUID) -> RecoveryCaseDetailResponse:
        """Approve pending action for a case (§15)."""
        case = await self.case_repo.get_by_id(case_id)
        if not case or case.status != RecoveryCaseStatus.PENDING_APPROVAL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case is not in PENDING_APPROVAL status")

        approval = await self.case_repo.get_pending_approval(case_id)
        if approval:
            approval.status = ApprovalStatus.APPROVED
            approval.decided_by_user_id = user_id

        case.status = RecoveryCaseStatus.EXECUTING
        await self.case_repo.add_audit_log(
            correlation_id=case.correlation_id,
            event_type="APPROVAL_APPROVED",
            payload={"decided_by_user_id": str(user_id)}
        )
        await self.session.commit()
        return await self.get_case_detail(case_id)

    async def reject_case(self, case_id: uuid.UUID, user_id: uuid.UUID) -> RecoveryCaseDetailResponse:
        """Reject pending action for a case (§15)."""
        case = await self.case_repo.get_by_id(case_id)
        if not case or case.status != RecoveryCaseStatus.PENDING_APPROVAL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Case is not in PENDING_APPROVAL status")

        approval = await self.case_repo.get_pending_approval(case_id)
        if approval:
            approval.status = ApprovalStatus.REJECTED
            approval.decided_by_user_id = user_id

        case.status = RecoveryCaseStatus.CLOSED
        await self.case_repo.add_audit_log(
            correlation_id=case.correlation_id,
            event_type="APPROVAL_REJECTED",
            payload={"decided_by_user_id": str(user_id)}
        )
        await self.session.commit()
        return await self.get_case_detail(case_id)

    async def get_case_timeline(self, case_id: uuid.UUID) -> List[AuditLogTimelineItem]:
        """Fetch ordered audit logs for case correlation_id (§9.2)."""
        case = await self.case_repo.get_by_id(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recovery case not found")

        logs = await self.case_repo.get_timeline_by_correlation_id(case.correlation_id)
        return [
            AuditLogTimelineItem(
                id=l.id,
                merchant_id=l.merchant_id,
                correlation_id=l.correlation_id,
                event_type=l.event_type,
                payload=l.payload,
                created_at=l.created_at
            ) for l in logs
        ]

    async def get_dashboard_summary(self) -> DashboardSummaryResponse:
        """Compute dashboard metrics (§1.3 & §19)."""
        cases, total = await self.case_repo.list_cases_paginated(limit=5, offset=0)
        payments, _ = await self.payment_repo.list_payments_paginated(limit=100, offset=0)

        failed_revenue = sum(p.amount_minor for p in payments if p.status == PaymentStatus.FAILED)
        recovered_revenue = sum(p.amount_minor for p in payments if p.status == PaymentStatus.RECOVERED)
        recoverable_revenue = failed_revenue + recovered_revenue
        
        recovery_rate = (recovered_revenue / recoverable_revenue) if recoverable_revenue > 0 else 0.0
        pending_cases = sum(1 for c in cases if c.status in (RecoveryCaseStatus.OPEN, RecoveryCaseStatus.PENDING_APPROVAL))
        escalations = sum(1 for c in cases if c.status == RecoveryCaseStatus.PENDING_APPROVAL)

        recent_items = [
            RecoveryCaseListItemResponse(
                id=c.id,
                merchant_id=c.merchant_id,
                payment_id=c.payment_id,
                status=c.status,
                correlation_id=c.correlation_id,
                created_at=c.created_at,
                updated_at=c.updated_at
            ) for c in cases
        ]

        return DashboardSummaryResponse(
            failed_revenue_minor=failed_revenue,
            recoverable_revenue_minor=recoverable_revenue,
            recovered_revenue_minor=recovered_revenue,
            recovery_rate=round(recovery_rate, 4),
            pending_cases=pending_cases,
            escalations=escalations,
            recent_cases=recent_items
        )
