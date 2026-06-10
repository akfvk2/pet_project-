import pytest
import pytest_asyncio
import fakeredis.aioredis
from unittest.mock import AsyncMock
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport
from alembic.config import Config
from alembic import command
from src.application import get_app
from src.db import get_session
import src.cache as cache_module
from src.models.base_model import Base
from src.models.user import UserModel
from src.models.profile import ProfileModel
from src.models.author import Author
from src.models.book import Book
from src.models.student import Students
from src.models.course import Course
import os

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def db_url(postgres_container):
    url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://"
    )
    os.environ["postgres_url"] = url  # env.py подхватит этот URL
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    return url


@pytest_asyncio.fixture
async def db_session(db_url):
    engine = create_async_engine(db_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock()
    redis.delete = AsyncMock()
    return redis


@pytest.fixture
def mock_order_client():
    client = AsyncMock()
    client.get_orders_by_user_id = AsyncMock(return_value=[])
    client.create_order = AsyncMock(return_value={"id": str(__import__('uuid').uuid4()), "title": "test order", "price": 0.0, "description": "", "status": "pending"})
    return client


@pytest_asyncio.fixture
async def client(db_session):
    app = get_app()

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    cache_module.redis_client._client = fakeredis.aioredis.FakeRedis()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac

    app.dependency_overrides.clear()