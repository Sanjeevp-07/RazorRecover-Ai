import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.merchant_user import MerchantUser

class UserRepository:
    """Repository for querying merchant_users."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[MerchantUser]:
        """Fetch user by unique email."""
        stmt = select(MerchantUser).where(MerchantUser.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[MerchantUser]:
        """Fetch user by ID."""
        stmt = select(MerchantUser).where(MerchantUser.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, user: MerchantUser) -> MerchantUser:
        """Add new merchant user."""
        self.session.add(user)
        await self.session.flush()
        return user
