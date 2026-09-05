from typing import AsyncGenerator
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from pathlib import Path
from app.core.config import settings

logger = logging.getLogger("razorrecover.db")

_DB_PATH = (Path(__file__).resolve().parent.parent.parent / "razorrecover.db").as_posix()

class Base(DeclarativeBase):
    """Base ORM model class."""
    pass

# Sync Engine & Session Factory for synchronous scripts / Celery workers
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL if not settings.SYNC_DATABASE_URL.startswith("sqlite") else f"sqlite:///{_DB_PATH}",
    echo=False,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 1} if "postgresql" in settings.SYNC_DATABASE_URL else {}
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

def get_engine_and_factory(db_url: str):
    is_sqlite = db_url.startswith("sqlite")
    connect_args = {} if is_sqlite else {"timeout": 3.0, "command_timeout": 3.0}
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    return engine, session_factory

# Initial primary engine
async_engine, AsyncSessionLocal = get_engine_and_factory(settings.DATABASE_URL)

async def init_db():
    """Initialize database tables, ensuring fallback to SQLite if primary DB is unavailable."""
    global async_engine, AsyncSessionLocal
    import app.models  # Ensure all ORM models are registered with Base

    try:
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.warning(f"Failed to connect to primary DB ({settings.DATABASE_URL}): {exc}. Falling back to SQLite.")
        sqlite_url = f"sqlite+aiosqlite:///{_DB_PATH}"
        async_engine, AsyncSessionLocal = get_engine_and_factory(sqlite_url)
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully using fallback SQLite.")

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing async DB session in HTTP routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
