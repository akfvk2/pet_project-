from src.repositories.BaseRepository import BaseRepository
from src.models.user import UserModel
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserModel, session)