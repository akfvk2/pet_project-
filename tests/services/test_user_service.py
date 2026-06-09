import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.services.user_service import UserService
from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.exceptions.not_found import NotFoundException
from src.models.user import UserModel
import src.services.user_service as svc_module


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.setex = AsyncMock()
    redis.delete = AsyncMock()
    return redis


@pytest.fixture
def user_service(mock_redis):
    service = UserService(session=AsyncMock())
    svc_module.redis_client = mock_redis
    return service


@pytest.fixture
def sample_user():
    user = UserModel(username="testuser", email="test@gmail.com", age=25)
    user.id = uuid4()
    user.profile = None
    return user


class TestGetUserById:
    async def test_cache_miss_fetches_from_db(self, user_service, mock_redis, sample_user):
        user_service.users_repo.get_by_id = AsyncMock(return_value=sample_user)

        result = await user_service.get_user_by_id(sample_user.id)

        assert result.username == "testuser"
        mock_redis.setex.assert_called_once()

    async def test_cache_hit_skips_db(self, user_service, mock_redis, sample_user):
        user_read = UserRead.model_validate(sample_user)
        mock_redis.get = AsyncMock(return_value=user_read.model_dump_json())
        user_service.users_repo.get_by_id = AsyncMock()

        await user_service.get_user_by_id(sample_user.id)

        user_service.users_repo.get_by_id.assert_not_called()  # БД не трогали

    async def test_not_found_raises_exception(self, user_service):
        user_service.users_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await user_service.get_user_by_id(uuid4())


class TestCreateUser:
    async def test_create_returns_user_read(self, user_service, sample_user):
        user_service.users_repo.create = AsyncMock(return_value=sample_user)
        user_in = UserCreate(username="testuser", email="test@gmail.com", age=25)

        result = await user_service.create_user(user_in)

        assert result.username == "testuser"



class TestUpdateUser:
    async def test_update_success(self, user_service, sample_user):
        user_service.users_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.users_repo.update = AsyncMock(return_value=sample_user)

        user_in = UserUpdate(username="updated", email="updated@gmail.com", age=30)
        result = await user_service.update_user(sample_user.id, user_in)

        assert result.username == "updated"
        user_service.users_repo.update.assert_called_once()

    async def test_update_clears_cache(self, user_service, mock_redis, sample_user):
        user_service.users_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.users_repo.update = AsyncMock(return_value=sample_user)

        await user_service.update_user(
            sample_user.id,
            UserUpdate(username="updated", email="updated@gmail.com", age=30)
        )

        mock_redis.delete.assert_called_once_with(f"user:{sample_user.id}")

    async def test_update_not_found(self, user_service):
        user_service.users_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await user_service.update_user(
                uuid4(),
                UserUpdate(username="updated", email="updated@gmail.com", age=30)
            )


class TestDeleteUser:
    async def test_delete_clears_cache(self, user_service, mock_redis, sample_user):
        user_service.users_repo.get_by_id = AsyncMock(return_value=sample_user)
        user_service.users_repo.delete = AsyncMock()

        await user_service.delete_user(sample_user.id)

        mock_redis.delete.assert_called_once_with(f"user:{sample_user.id}")