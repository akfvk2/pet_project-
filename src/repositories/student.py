from src.repositories.repositories import BaseRepository
from src.models import base_model
from sqlalchemy.ext.asyncio import AsyncSession


class StudentRepository(BaseRepository[base_model.Students]):
    def __init__(self, session: AsyncSession):
        super().__init__(base_model.Students, session)