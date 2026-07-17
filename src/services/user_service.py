from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserUpdate, UserRead
from src.repositories.user import UserRepository
from src.cache import redis_client
from uuid import UUID, uuid4
import logging
from src.clients.order_client import OrderServiceClient
from src.schemas.users import UserWithOrdersRead, UserCreateWithOrder
from src.schemas.orders import OrderResponse
from src.config import settings
from typing import TypedDict
from src.exceptions.service_exception import ServiceException
from src.exceptions.service_unreachable import ServiceUnreachableException
from src.models.pending_order_confirmation import PendingOrderConfirmationModel

logger = logging.getLogger(__name__)



class UserLogExtra(TypedDict):
    user_id: UUID

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users_repo = UserRepository(self.session)
        self.order_client = OrderServiceClient()


    def _cache_key(self, user_id: UUID) -> str:
        return f"user:{user_id}"

    def _to_response(self, user_data: UserRead, orders: list[OrderResponse]) -> UserWithOrdersRead:
        return UserWithOrdersRead(
            **user_data.model_dump(),
            orders=orders
        )

    async def _get_user_or_fail(self, user_id: UUID):
        return await self.users_repo.get_by_id_or_fail(
            user_id, "User", extra=UserLogExtra(user_id=user_id)
        )

    async def create_user(self, user_in: UserCreateWithOrder) -> UserWithOrdersRead:
        user_entity = user_in.to_model()
        db_user = await self.users_repo.create(user_entity)
        reference_id = uuid4()
        orders: list[OrderResponse] = []
        try:
            order = await self.order_client.create_order(
                user=db_user,
                order_in=user_in.to_order_create(),
                reference_id=reference_id
            )
            orders = [order]
        except ServiceException:
            self.session.add(PendingOrderConfirmationModel(user_id=db_user.id, reference_id=reference_id))

        user_data = UserRead.model_validate(db_user)
        return self._to_response(user_data, orders)

    async def update_user(self, user_id: UUID, user_in: UserUpdate):
        users_entity = await self._get_user_or_fail(user_id)
        user_in.update_model(users_entity)
        updated_user = await self.users_repo.update(users_entity)
        updated_result = UserRead.model_validate(updated_user)
        await redis_client.setex(self._cache_key(user_id), settings.cache_ttl, updated_result.model_dump_json())
        return updated_result

    async def delete_user(self, user_id: UUID):
        users_entity = await self._get_user_or_fail(user_id)
        await self.users_repo.delete(users_entity)
        await redis_client.delete(self._cache_key(user_id))
        return True

    async def get_user_with_orders(self, user_id: UUID):
        user_entity = await self._get_user_or_fail(user_id)
        orders = await self.order_client.get_orders_by_user_id(user_id)
        user_data = UserRead.model_validate(user_entity)
        return self._to_response(user_data, orders)

