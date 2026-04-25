from src.repositories.BaseRepository import BaseRepository
from src.models.student import Students
from sqlalchemy.ext.asyncio import AsyncSession


class StudentRepository(BaseRepository[Students]):
    def __init__(self, session: AsyncSession):
        super().__init__(Students, session)