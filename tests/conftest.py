import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.models.base_model import Base
from src.models.user import UserModel
from src.models.profile import ProfileModel


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def db_url(postgres_container):
    url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://"
    )
    async def _create_tables():
        engine = create_async_engine(url, poolclass=NullPool)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(_create_tables())
    return url


@pytest_asyncio.fixture
async def db_session(db_url):
    engine = create_async_engine(db_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()