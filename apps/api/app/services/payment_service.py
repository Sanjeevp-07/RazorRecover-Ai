import uuid
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.payment_repository import PaymentRepository
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentResponse

class PaymentService:
    """Service layer for payment queries and operations."""
    def __init__(self, session: AsyncSession, merchant_id: uuid.UUID):
        self.session = session
        self.merchant_id = merchant_id
        self.payment_repo = PaymentRepository(session, merchant_id)

    async def list_payments(
        self,
        status_filter: Optional[PaymentStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[PaymentResponse], int]:
        """List paginated payments for merchant."""
        offset = (page - 1) * page_size
        payments, total = await self.payment_repo.list_payments_paginated(
            status_filter=status_filter,
            limit=page_size,
            offset=offset
        )
        items = [
            PaymentResponse(
                id=p.id,
                merchant_id=p.merchant_id,
                order_id=p.order_id,
                customer_id=p.customer_id,
                provider_payment_id=p.provider_payment_id,
                amount_minor=p.amount_minor,
                currency=p.currency,
                status=p.status,
                failure_reason=p.failure_reason,
                method=p.method,
                created_at=p.created_at,
                updated_at=p.updated_at
            ) for p in payments
        ]
        return items, total

    async def get_payment(self, payment_id: uuid.UUID) -> PaymentResponse:
        """Fetch payment details by ID."""
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        return PaymentResponse(
            id=payment.id,
            merchant_id=payment.merchant_id,
            order_id=payment.order_id,
            customer_id=payment.customer_id,
            provider_payment_id=payment.provider_payment_id,
            amount_minor=payment.amount_minor,
            currency=payment.currency,
            status=payment.status,
            failure_reason=payment.failure_reason,
            method=payment.method,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )
