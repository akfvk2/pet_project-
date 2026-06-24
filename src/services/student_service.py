from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.student import StudentRepository
from src.exceptions.not_found import NotFoundException
from src.models import student, course
from src.cache import redis_client
from src.schemas import students
from uuid import UUID
import logging
import json
from src.config import settings
from typing import TypedDict

logger = logging.getLogger(__name__)

class StudentLogExtra(TypedDict):
    student_id: UUID


class StudentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.students_repo = StudentRepository(self.session)

    def _cache_key(self, student_id: UUID) -> str:
        return f"student:{student_id}"

    async def _get_student_or_fail(self, student_id: UUID):
        student_entity = await self.students_repo.get_by_id(student_id)
        if not student_entity:
            logger.error(
                "Entity 'Student' not found",
                extra=StudentLogExtra(student_id=student_id)
            )
            raise NotFoundException(f"Student with id {student_id} not found")
        return student_entity

    async def create_student(self, student_in: students.StudentCreate):
        students_entity = student_in.to_model()
        db_student = await self.students_repo.create(students_entity)
        return db_student

    async def get_student_by_id(self, student_id: UUID):
        cache_key = self._cache_key(student_id)
        cached = await redis_client.get(cache_key)
        if cached:
            logger.info(f"Cache hit for student {student_id}")
            return json.loads(cached)

        student_entity = await self._get_student_or_fail(student_id)
        schema = students.StudentRead.model_validate(student_entity)
        await redis_client.setex(cache_key, settings.cache_ttl, schema.model_dump_json())
        return student_entity

    async def update_student(self, student_id: UUID, student_in: students.StudentUpdate):
        students_entity = await self._get_student_or_fail(student_id)
        student_in.update_model(students_entity)
        updated_student = await self.students_repo.update(students_entity)
        schema = students.StudentRead.model_validate(updated_student)
        await redis_client.setex(self._cache_key(student_id), settings.cache_ttl, schema.model_dump_json())
        return updated_student

    async def delete_student(self, student_id: UUID):
        students_entity = await self._get_student_or_fail(student_id)
        await self.students_repo.delete(students_entity)
        await redis_client.delete(self._cache_key(student_id))
        return True
