import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.merchant import Merchant

class MerchantRepository:
    """Repository for querying merchants."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, merchant_id: uuid.UUID) -> Optional[Merchant]:
        """Fetch merchant by ID."""
        stmt = select(Merchant).where(Merchant.id == merchant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, merchant: Merchant) -> Merchant:
        """Create new merchant."""
        self.session.add(merchant)
        await self.session.flush()
        return merchant
