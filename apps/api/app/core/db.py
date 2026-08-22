from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

# API Async Engine & Session Factory (asyncpg)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args={"timeout": 0.5, "command_timeout": 0.5}
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Celery Worker Sync Engine & Session Factory (psycopg2)
# Explicit requirement (§3): workers use sync driver; no shared async engine across process boundary.
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 1}
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    """Base ORM model class."""
    pass

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing async DB session in HTTP routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
