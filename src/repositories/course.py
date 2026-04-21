from src.repositories.repositories import BaseRepository
from src.models import base_model
from sqlalchemy.ext.asyncio import AsyncSession

class CourseRepository(BaseRepository[base_model.Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(base_model.Course, session)