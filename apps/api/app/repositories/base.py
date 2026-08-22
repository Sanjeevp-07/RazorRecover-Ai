import uuid
from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """
    Mandatory Base Repository (§6 & §7.2).
    Requires a merchant_id on instantiation to ensure EVERY database query
    is automatically scoped by the authenticated merchant's ID.
    """
    def __init__(self, model: Type[ModelType], session: AsyncSession, merchant_id: uuid.UUID):
        self.model = model
        self.session = session
        self.merchant_id = merchant_id

    async def get_by_id(self, id: uuid.UUID) -> Optional[ModelType]:
        """Fetch a single record by ID, scoped by merchant_id."""
        stmt = select(self.model).where(
            self.model.id == id,
            getattr(self.model, "merchant_id") == self.merchant_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 20, offset: int = 0) -> List[ModelType]:
        """List records scoped by merchant_id."""
        stmt = select(self.model).where(
            getattr(self.model, "merchant_id") == self.merchant_id
        ).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, instance: ModelType) -> ModelType:
        """Add record ensuring merchant_id is set."""
        if hasattr(instance, "merchant_id") and getattr(instance, "merchant_id") is None:
            setattr(instance, "merchant_id", self.merchant_id)
        self.session.add(instance)
        await self.session.flush()
        return instance
