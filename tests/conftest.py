import pytest
import pytest_asyncio
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
from testcontainers.redis import RedisContainer
from src.cache import RedisClient
import respx
import httpx
from uuid import uuid4 as _uuid4
from src.cache import RedisClient
from src.config import settings
from src.clients.order_client import OrderServiceClient

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

@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7") as container:
        yield container


@pytest.fixture(scope="session")
def redis_url(redis_container):
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    return f"redis://{host}:{port}"


@pytest_asyncio.fixture
async def db_session(db_url):
    engine = create_async_engine(db_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def redis_client(redis_url):
    client = RedisClient(redis_url)
    yield client
    await client._client.flushall()


@pytest.fixture
def order_client():
    client = OrderServiceClient()
    with respx.mock(base_url=settings.order_service_url, assert_all_called=False) as mock:
        mock.get(settings.orders_path).mock(return_value=httpx.Response(200, json=[]))
        mock.post(settings.orders_path).mock(return_value=httpx.Response(201, json={
            "id": str(_uuid4()),
            "title": "test order",
            "price": 0.0,
            "description": "",
            "status": "pending",
        }))
        yield client


@pytest_asyncio.fixture
async def client(db_session, redis_url):
    app = get_app()
    async def override_get_session():
        yield db_session
    app.dependency_overrides[get_session] = override_get_session
    cache_module.redis_client = RedisClient(redis_url)
    with respx.mock(base_url=settings.order_service_url, assert_all_called=False) as mock:
        mock.post(settings.orders_path).mock(return_value=httpx.Response(201, json={
            "id": str(_uuid4()),
            "title": "Test Order",
            "price": 10.0,
            "description": "",
            "status": "pending"
        }))
        mock.get(settings.orders_path).mock(
            return_value=httpx.Response(200, json=[])
        )

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            follow_redirects=True
        ) as ac:
            yield ac

    app.dependency_overrides.clear()