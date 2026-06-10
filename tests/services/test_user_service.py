import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.services.user_service import UserService
from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.exceptions.not_found import NotFoundException
from src.models.user import UserModel
import src.services.user_service as svc_module
from src.schemas.users import UserCreate, UserRead, UserUpdate, UserCreateWithOrder


@pytest.fixture
def user_service(mock_redis, mock_order_client):
    service = UserService(session=AsyncMock())
    svc_module.redis_client = mock_redis
    service.order_client = mock_order_client
    return service


@pytest.fixture
def sample_user():
    user = UserModel(username="testuser", email="test@gmail.com", age=25)
    user.id = uuid4()
    user.profile = None
    return user


class TestGetUserWithOrders:
    async def test_fetches_from_db(self, user_service, sample_user):
        user_service.users_repo.get_by_id = AsyncMock(return_value=sample_user)

        result = await user_service.get_user_with_orders(sample_user.id)

        assert result.username == "testuser"
        user_service.users_repo.get_by_id.assert_called_once()

    async def test_not_found_raises_exception(self, user_service):
        user_service.users_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NotFoundException):
            await user_service.get_user_with_orders(uuid4())


class TestCreateUser:
    async def test_create_returns_user_read(self, user_service, sample_user):
        user_service.users_repo.create = AsyncMock(return_value=sample_user)
        user_in = UserCreateWithOrder(
            username="testuser",
            email="test@gmail.com",
            age=25,
            order_title="Test Order",
            order_price=10.0
        )
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

        mock_redis.setex.assert_called_once()

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