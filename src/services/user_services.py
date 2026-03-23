from sqlalchemy.ext.asyncio import AsyncSession
from src.models.shemas import users_s
from src.repositories.repositories import UserRepository
from src.exceptions import NotFoundException
from src.models import users

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session




    async def create_user(self, user_in: users_s.UserCreate):
        user_repo = UserRepository(self.session)
        users_entity = users.UserModel(**user_in.model_dump())
        db_user = await user_repo.create(users_entity)
        return  users_s.UserRead.model_validate(db_user)


    async def get_user_by_id(self, user_id: int):
        user_repo = UserRepository(self.session)
        user_entity = await user_repo.get_by_id(user_id)
        if not user_entity:
            raise NotFoundException("User not found")
        return users_s.UserRead.model_validate(user_entity)


    async def update_user(self, user_id: int, user_in: users_s.UserUpdate):
        users_repo = UserRepository(self.session)
        users_entity = await users_repo.get_by_id(user_id)
        if not users_entity:
            raise NotFoundException("User not found")
        updated_data = user_in.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(users_entity, key, value)
        updated_user = await users_repo.update(users_entity)
        return users_s.UserRead.model_validate(updated_user)


    async def delete_user(self, user_id: int):
        user_repo = UserRepository(self.session)
        users_entity = await user_repo.get_by_id(user_id)
        if not users_entity:
            raise NotFoundException("User not found")
        await user_repo.delete(users_entity)
        return True