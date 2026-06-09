from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserCreate, UserUpdate, UserRead
from src.repositories.user import UserRepository
from src.exceptions.not_found import NotFoundException
from src.cache import redis_client
from uuid import UUID
import logging
import json
from src.clients.order_client import OrderServiceClient
from src.schemas.users import UserWithOrdersRead, OrderResponse
from src.exceptions.base import AppException

logger = logging.getLogger(__name__)
CACHE_TTL = 3600

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users_repo = UserRepository(self.session)

    def _cache_key(self, user_id: UUID) -> str:
        return f"user:{user_id}"

    async def _get_user_or_fail(self, user_id: UUID):
        user_entity = await self.users_repo.get_by_id(user_id)
        if not user_entity:
            logger.error(
                f"Entity 'User' with id {user_id} not found",
                extra={"user_id": user_id}
            )
            raise NotFoundException("User not found")
        return user_entity

    async def create_user(self, user_in: UserCreate) -> UserRead:
        user_entity = user_in.to_model()
        db_user = await self.users_repo.create(user_entity)
        return UserRead.model_validate(db_user)

    async def get_user_by_id(self, user_id: UUID) -> UserRead:
        cache_key = self._cache_key(user_id)

        cached = await redis_client.get(cache_key)
        if cached:
            logger.info(f"Cache hit for user {user_id}")
            return UserRead.model_validate(json.loads(cached))
        user_entity = await self._get_user_or_fail(user_id)
        if user_entity.profile:
            user_entity.profile.user = None
        result = UserRead.model_validate(user_entity)
        await redis_client.setex(cache_key, CACHE_TTL, result.model_dump_json())
        return result

    async def update_user(self, user_id: UUID, user_in: UserUpdate):
        users_entity = await self._get_user_or_fail(user_id)
        user_in.update_model(users_entity)
        updated_user = await self.users_repo.update(users_entity)
        await redis_client.delete(self._cache_key(user_id))
        return UserRead.model_validate(updated_user)

    async def delete_user(self, user_id: UUID):
        users_entity = await self._get_user_or_fail(user_id)
        await self.users_repo.delete(users_entity)
        await redis_client.delete(self._cache_key(user_id))
        return True

    async def get_user_with_orders(self, user_id: UUID):
        user_entity = await self._get_user_or_fail(user_id)
        if user_entity.profile:
            user_entity.profile.user = None

        client = OrderServiceClient()
        orders = await client.get_orders_by_user_id(user_id)

        user_data = UserRead.model_validate(user_entity)
        return UserWithOrdersRead(
            **user_data.model_dump(),
            orders=[OrderResponse(**o) for o in orders]
        )

    async def create_order_for_user(self, user_id: UUID, order_in):
        await self._get_user_or_fail(user_id)

        client = OrderServiceClient()
        order = await client.create_order(
            user_id=user_id,
            title=order_in.title,
            price=order_in.price,
            description=order_in.description,
        )
        if not order:
            raise AppException(status_code=503, message="Order service unavailable")
        return OrderResponse(**order)