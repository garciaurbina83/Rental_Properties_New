"""
Database configuration module
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import AsyncGenerator

from ..core.config import settings

# Replace postgresql:// with postgresql+asyncpg:// for async support
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True
)

SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def init_db() -> None:
    """
    Initialize database by creating all tables
    """
    # Import all models here to ensure they are registered with Base
    # We import them here to avoid circular imports
    from ..models.property import Property
    from ..models.tenant import Tenant

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
