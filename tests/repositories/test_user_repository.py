import pytest_asyncio
from uuid import uuid4
from src.repositories.user import UserRepository
from src.models.user import UserModel


@pytest_asyncio.fixture
async def repo(db_session):
    return UserRepository(db_session)


class TestUserRepository:
    async def test_create_user(self, repo):
        user = UserModel(username="testuser", email="test@gmail.com", age=25)
        created = await repo.create(user)
        assert created.id is not None
        assert created.username == "testuser"

    async def test_get_by_id(self, repo):
        user = UserModel(username="testuser", email="test@gmail.com", age=25)
        created = await repo.create(user)
        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.username == "testuser"

    async def test_get_by_id_not_found(self, repo):
        found = await repo.get_by_id(uuid4())
        assert found is None

    async def test_update_user(self, repo):
        user = UserModel(username="testuser", email="test@gmail.com", age=25)
        created = await repo.create(user)
        created.username = "updated"
        created.age = 30
        updated = await repo.update(created)
        assert updated.username == "updated"
        assert updated.age == 30

    async def test_soft_delete(self, repo):
        user = UserModel(username="testuser", email="test@gmail.com", age=25)
        created = await repo.create(user)
        await repo.delete(created)
        assert created.is_deleted is True