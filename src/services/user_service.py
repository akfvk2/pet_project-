from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.users import UserUpdate, UserRead
from src.repositories.user import UserRepository
from src.cache import redis_client
from uuid import UUID, uuid4
import logging
from src.clients.order_client import OrderServiceClient
from src.schemas.users import UserWithOrdersRead, UserCreateWithOrder
from src.config import settings
from typing import TypedDict
from src.exceptions.external_service_exception import ExternalServiceException
from src.services.service_helpers import get_by_id_or_fail
from src.mappers.user_mapper import UserMapper
from src.schemas.users import OrderConfirmationStatus
from src.repositories.pending_confirmation import PendingConfirmationRepository
from src.unit_of_work import UnitOfWork



logger = logging.getLogger(__name__)



class UserLogExtra(TypedDict):
    user_id: UUID

class UserService:
    def __init__(self, session: AsyncSession, order_client: OrderServiceClient, unit_of_work_cls: type[UnitOfWork] = UnitOfWork):
        self.session = session
        self.users_repo = UserRepository(self.session)
        self.order_client = order_client
        self.pending_confirmation_repo = PendingConfirmationRepository(self.session)
        self.unit_of_work_cls = unit_of_work_cls


    def _cache_key(self, user_id: UUID) -> str:
        return f"user:{user_id}"


    async def _get_user_or_fail(self, user_id: UUID):
        return await get_by_id_or_fail(
            self.users_repo, user_id, "User", extra=UserLogExtra(user_id=user_id)
        )

    async def create_user(self, user_in: UserCreateWithOrder) -> UserWithOrdersRead:
        user_entity = user_in.to_model()
        reference_id = uuid4()
        async with self.unit_of_work_cls(self.session):
            db_user = await self.users_repo.create(user_entity)
            self.pending_confirmation_repo.register_pending(db_user.id, reference_id)
        user_data = UserRead.model_validate(db_user)
        try:
            order = await self.order_client.create_order(
                user_id=db_user.id,
                order_in=user_in.to_order_create(),
                reference_id=reference_id
            )
        except ExternalServiceException:
            return UserMapper.to_user_with_orders(user_data, [], OrderConfirmationStatus.PENDING)
        await self.pending_confirmation_repo.resolve_pending(reference_id)
        return UserMapper.to_user_with_orders(user_data, [order], OrderConfirmationStatus.CONFIRMED)

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
        user_data = UserRead.model_validate(user_entity)
        await self.session.close()
        orders = await self.order_client.get_orders_by_user_id(user_id)
        return UserMapper.to_user_with_orders(user_data, orders)

