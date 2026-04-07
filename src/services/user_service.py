from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schemas.users import UserCreate, UserUpdate, UserRead
from src.repositories.repositories import StudentRepository
from src.exceptions.common import NotFoundException
from src.models import users
from src.models.schemas import users
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.students_repo = StudentRepository(self.session)



    async def create_user(self, user_in: UserCreate):
        users_entity = users.UserModel(**user_in.model_dump())
        db_user = await self.students_repo.create(users_entity)
        return  UserRead.model_validate(db_user)


    async def get_user_by_id(self, user_id: uuid4()):
        user_entity = await self.students_repo.get_by_id(user_id)
        if not user_entity:
            logger.error(
                f"Entity 'User' with id {user_id} not found",
                extra={"user_id": user_id}
            )
            raise NotFoundException("User not found")
        return UserRead.model_validate(user_entity)


    async def update_user(self, user_id: uuid4(), user_in: UserUpdate):
        users_entity = await self.students_repo.get_by_id(user_id)
        if not users_entity:
            logger.error(
                f"Entity 'User' with id {user_id} not found",
                extra={"user_id": user_id}
            )
            raise NotFoundException("User not found")
        updated_data = user_in.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(users_entity, key, value)
        updated_user = await self.students_repo.update(users_entity)
        return UserRead.model_validate(updated_user)


    async def delete_user(self, user_id: uuid4()):
        users_entity = await self.students_repo.get_by_id(user_id)
        if not users_entity:
            logger.error(
                f"Entity 'User' with id {user_id} not found",
                extra={"user_id": user_id}
            )
            raise NotFoundException("User not found")
        await self.students_repo.delete(users_entity)
        return True