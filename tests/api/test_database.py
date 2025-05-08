import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_async_session, Base, engine


@pytest.mark.asyncio
async def test_get_async_session():
    async for session in get_async_session():
        assert isinstance(session, AsyncSession)
        break


@pytest.mark.asyncio
async def test_create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)