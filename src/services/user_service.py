from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import UserCreate, UserUpdate, UserRead
from src.repositories.user import UserRepository
from src.exceptions.not_found import NotFoundException
from src.models import user , profile
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.students_repo = UserRepository(self.session)

    async def _get_user_or_fail(self, user_id: UUID):
        user_entity = await self.students_repo.get_by_id(user_id)
        if not user_entity:
            logger.error(
                f"Entity 'User' with id {user_id} not found",
                extra={"user_id": user_id}
            )
            raise NotFoundException("User not found")
        return user_entity

    async def create_user(self, user_in: UserCreate) -> UserRead:
        user_data = user_in.model_dump(exclude={"profile"})
        profile_data = user_in.profile
        user_entity = user.UserModel(**user_data)
        profile_entity = profile.ProfileModel(**profile_data.model_dump())
        user_entity.profile = profile_entity
        db_user = await self.students_repo.create(user_entity)
        await self.session.flush()
        await self.session.refresh(db_user)
        return UserRead.model_validate(db_user)

    async def get_user_by_id(self, user_id: UUID):
        user_entity = await self._get_user_or_fail(user_id)
        return UserRead.model_validate(user_entity)

    async def update_user(self, user_id: UUID, user_in: UserUpdate):
        users_entity = await self._get_user_or_fail(user_id)
        updated_data = user_in.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(users_entity, key, value)
        updated_user = await self.students_repo.update(users_entity)
        return UserRead.model_validate(updated_user)

    async def delete_user(self, user_id: UUID):
        users_entity = await self._get_user_or_fail(user_id)
        await self.students_repo.delete(users_entity)
        return True