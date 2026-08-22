import uuid
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.repositories.base import BaseRepository
from app.models.payment import Payment, PaymentStatus
from app.models.order import Order

class PaymentRepository(BaseRepository[Payment]):
    """Repository for managing payments and orders."""
    def __init__(self, session: AsyncSession, merchant_id: uuid.UUID):
        super().__init__(Payment, session, merchant_id)

    async def get_by_provider_id(self, provider_payment_id: str) -> Optional[Payment]:
        """Fetch payment by Razorpay payment ID."""
        stmt = select(Payment).where(
            Payment.provider_payment_id == provider_payment_id,
            Payment.merchant_id == self.merchant_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_payments_paginated(
        self,
        status_filter: Optional[PaymentStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Payment], int]:
        """List payments with pagination and status filtering."""
        query = select(Payment).where(Payment.merchant_id == self.merchant_id)
        count_query = select(func.count(Payment.id)).where(Payment.merchant_id == self.merchant_id)

        if status_filter:
            query = query.where(Payment.status == status_filter)
            count_query = count_query.where(Payment.status == status_filter)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit)
        items_res = await self.session.execute(query)
        items = list(items_res.scalars().all())

        return items, total

    async def get_order_by_provider_id(self, provider_order_id: str) -> Optional[Order]:
        """Fetch order by Razorpay order ID."""
        stmt = select(Order).where(
            Order.provider_order_id == provider_order_id,
            Order.merchant_id == self.merchant_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
