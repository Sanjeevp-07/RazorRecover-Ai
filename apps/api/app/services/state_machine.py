import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status

from app.models.payment import Payment, PaymentStatus
from app.models.recovery_case import RecoveryCase, RecoveryCaseStatus
from app.models.action_execution import ActionExecution, ActionExecutionStatus
from app.models.approval import Approval, ApprovalStatus

# Valid Transition Mappings (§8)
VALID_PAYMENT_TRANSITIONS = {
    PaymentStatus.CREATED: {PaymentStatus.ATTEMPTED},
    PaymentStatus.ATTEMPTED: {PaymentStatus.FAILED, PaymentStatus.CAPTURED},
    PaymentStatus.FAILED: {PaymentStatus.RECOVERED},
    PaymentStatus.CAPTURED: set(),  # Terminal
    PaymentStatus.RECOVERED: set(), # Terminal
}

VALID_CASE_TRANSITIONS = {
    RecoveryCaseStatus.OPEN: {RecoveryCaseStatus.ANALYZING},
    RecoveryCaseStatus.ANALYZING: {
        RecoveryCaseStatus.DENIED,
        RecoveryCaseStatus.PENDING_APPROVAL,
        RecoveryCaseStatus.EXECUTING
    },
    RecoveryCaseStatus.PENDING_APPROVAL: {
        RecoveryCaseStatus.EXECUTING,
        RecoveryCaseStatus.CLOSED,
        RecoveryCaseStatus.EXPIRED
    },
    RecoveryCaseStatus.EXECUTING: {
        RecoveryCaseStatus.RECOVERED,
        RecoveryCaseStatus.CLOSED
    },
    RecoveryCaseStatus.DENIED: set(),    # Terminal
    RecoveryCaseStatus.RECOVERED: set(), # Terminal
    RecoveryCaseStatus.CLOSED: set(),    # Terminal
    RecoveryCaseStatus.EXPIRED: set()    # Terminal
}

class StateMachineManager:
    """
    Explicit State Machine Transition Guard & Worker Claiming Manager (§8).
    Enforces deterministic state transitions and atomic row-locking concurrency controls (§17).
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def claim_case_for_analysis(self, case_id: uuid.UUID) -> Optional[RecoveryCase]:
        """
        Atomically claim a case for analysis by worker (§8.2 & §17).
        Uses `SELECT ... FOR UPDATE SKIP LOCKED` inside a transaction.
        """
        stmt = (
            select(RecoveryCase)
            .where(
                RecoveryCase.id == case_id,
                RecoveryCase.status == RecoveryCaseStatus.OPEN
            )
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        case = result.scalar_one_or_none()
        
        if not case:
            return None

        case.status = RecoveryCaseStatus.ANALYZING
        await self.session.commit()
        return case

    def validate_payment_transition(self, current_status: PaymentStatus, target_status: PaymentStatus) -> bool:
        """Validate if payment status transition is permitted."""
        allowed = VALID_PAYMENT_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    def validate_case_transition(self, current_status: RecoveryCaseStatus, target_status: RecoveryCaseStatus) -> bool:
        """Validate if recovery case status transition is permitted."""
        allowed = VALID_CASE_TRANSITIONS.get(current_status, set())
        return target_status in allowed

    async def transition_case_status(self, case: RecoveryCase, target_status: RecoveryCaseStatus) -> RecoveryCase:
        """Perform validated case status transition."""
        if not self.validate_case_transition(case.status, target_status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid case status transition from '{case.status.value}' to '{target_status.value}'"
            )
        case.status = target_status
        await self.session.commit()
        return case

    async def transition_payment_status(self, payment: Payment, target_status: PaymentStatus) -> Payment:
        """Perform validated payment status transition."""
        if not self.validate_payment_transition(payment.status, target_status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment status transition from '{payment.status.value}' to '{target_status.value}'"
            )
        payment.status = target_status
        await self.session.commit()
        return payment
