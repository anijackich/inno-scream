"""API database."""

from typing import AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from api.config import settings

Base = declarative_base()

engine = create_async_engine(settings.database.url, poolclass=NullPool)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_database():
    """Create database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get asynchrounous session."""
    async with AsyncSessionLocal() as session:
        yield session
