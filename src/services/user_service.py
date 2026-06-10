from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserCreate, UserUpdate, UserRead
from src.repositories.user import UserRepository
from src.exceptions.not_found import NotFoundException
from src.cache import redis_client
from uuid import UUID
import logging
import json
from src.clients.order_client import OrderServiceClient
from src.schemas.users import UserWithOrdersRead, UserCreateWithOrder
from src.schemas.orders import OrderResponse
from src.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users_repo = UserRepository(self.session)
        self.order_client = OrderServiceClient()

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

    async def create_user(self, user_in: UserCreateWithOrder) -> UserWithOrdersRead:
        user_entity = user_in.to_model()
        db_user = await self.users_repo.create(user_entity)
        user_data = UserRead.model_validate(db_user)

        order = await self.order_client.create_order(
            user_id=db_user.id,
            title=user_in.order_title,
            price=user_in.order_price,
            description=user_in.order_description,
        )

        return UserWithOrdersRead(
            **user_data.model_dump(),
            orders=[OrderResponse(**order)]
        )

    async def update_user(self, user_id: UUID, user_in: UserUpdate):
        users_entity = await self._get_user_or_fail(user_id)
        user_in.update_model(users_entity)
        updated_user = await self.users_repo.update(users_entity)
        updated_result = UserRead.model_validate(updated_user)
        try:
            await redis_client.setex(self._cache_key(user_id), settings.cache_ttl, updated_result.model_dump_json())
        except Exception as e:
            logger.warning(f"Redis unavailable, skipping cache update: {e}")
        return updated_result

    async def delete_user(self, user_id: UUID):
        users_entity = await self._get_user_or_fail(user_id)
        await self.users_repo.delete(users_entity)
        await redis_client.delete(self._cache_key(user_id))
        return True

    async def get_user_with_orders(self, user_id: UUID):
        user_entity = await self._get_user_or_fail(user_id)
        if user_entity.profile:
            user_entity.profile.user = None

        orders = await self.order_client.get_orders_by_user_id(user_id)

        user_data = UserRead.model_validate(user_entity)
        return UserWithOrdersRead(
            **user_data.model_dump(),
            orders=[OrderResponse(**o) for o in orders]
        )

