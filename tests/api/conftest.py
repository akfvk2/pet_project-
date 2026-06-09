import pytest_asyncio
import fakeredis.aioredis
from httpx import AsyncClient, ASGITransport
from src.application import get_app
from src.db import get_session
import src.services.user_service as svc_module
import src.services.author_service as author_svc
import src.services.student_service as student_svc

@pytest_asyncio.fixture
async def client(db_session):
    app = get_app()

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    svc_module.redis_client = fakeredis.aioredis.FakeRedis()
    author_svc.redis_client = fakeredis.aioredis.FakeRedis()
    student_svc.redis_client = fakeredis.aioredis.FakeRedis()

    async with AsyncClient(
    transport=ASGITransport(app=app),
    base_url="http://test",
    follow_redirects=True) as ac:
        yield ac

    app.dependency_overrides.clear()