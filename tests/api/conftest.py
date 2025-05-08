import pytest
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Load test environment variables
env_path = Path(__file__).parent / '.env.test'
load_dotenv(dotenv_path=env_path)

from src.api.database import Base  # noqa: E402
from src.api.models import Scream, Reaction  # noqa: E402


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def test_engine():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def override_get_session(test_session):
    async def _get_session():
        yield test_session

    return _get_session


@pytest.fixture
async def sample_scream(test_session):
    scream = Scream(user_id=123, text='Test scream')
    test_session.add(scream)
    await test_session.commit()
    await test_session.refresh(scream)

    yield scream


@pytest.fixture
async def sample_reaction(test_session, sample_scream):
    reaction = Reaction(user_id=456, scream_id=sample_scream.id, reaction='👍')
    test_session.add(reaction)
    await test_session.commit()
    await test_session.refresh(reaction)

    yield reaction
