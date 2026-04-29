from src.repositories.base_repository import BaseRepository
from src.models.course import Course
from sqlalchemy.ext.asyncio import AsyncSession

class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)