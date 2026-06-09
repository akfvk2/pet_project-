from src.repositories.base_repository import BaseRepository
from src.models.student import Students
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.course import Course


class StudentRepository(BaseRepository[Students]):
    def __init__(self, session: AsyncSession):
        super().__init__(Students, session)

    async def get_by_id(self, obj_id: UUID) -> Students | None:
        stmt = (
            select(Students)
            .where(Students.id == obj_id)
            .options(selectinload(Students.course).selectinload(Course.students))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()