from sqlalchemy.ext.asyncio import AsyncSession

from models import schemas
from repositories import repositories
from repositories.repositories import UserRepository


class UserService:
    @staticmethod
    async def create_user(session: AsyncSession, user_in: schemas.UserCreate):
        return await UserRepository.create(session, user_in)

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int):
        return await UserRepository.get_by_id(session, user_id)

    @staticmethod
    async def update_user(session: AsyncSession, user_id: int, user_in: schemas.UserUpdate):
        return await UserRepository.update(session, user_id, user_in)

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int):
        return await UserRepository.delete(session, user_id)