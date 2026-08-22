import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.webhook_event import WebhookEvent

class WebhookRepository(BaseRepository[WebhookEvent]):
    """Repository for managing webhook_events."""
    def __init__(self, session: AsyncSession, merchant_id: uuid.UUID):
        super().__init__(WebhookEvent, session, merchant_id)

    async def get_by_external_id(self, external_event_id: str) -> Optional[WebhookEvent]:
        """Fetch webhook event by Razorpay x-razorpay-event-id for deduplication (§10.2)."""
        stmt = select(WebhookEvent).where(
            WebhookEvent.external_event_id == external_event_id,
            WebhookEvent.merchant_id == self.merchant_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
