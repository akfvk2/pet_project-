from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.student import StudentRepository
from src.exceptions.not_found import NotFoundException
from src.models import student, course
from schemas import students
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class StudentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.students_repo = StudentRepository(self.session)

    async def _get_student_or_fail(self, student_id: UUID):
        student_entity = await self.students_repo.get_by_id(student_id)
        if not student_entity:
            logger.error(
                f"Entity 'Student' with id {student_id} not found",
                extra={"student_id": student_id}
            )
            raise NotFoundException(f"Student with id {student_id} not found")
        return student_entity

    async def create_student(self, student_in: students.StudentCreate):
        student_data = student_in.model_dump(exclude={"course"})
        course_data = student_in.course
        students_entity = student.Students(**student_data)
        course_entity = course.Course(**course_data.model_dump())
        students_entity.course = course_entity
        db_student = await self.students_repo.create(students_entity)
        await self.session.flush()
        await self.session.refresh(db_student)
        return  students.StudentRead.model_validate(db_student)

    async def get_student_by_id(self, student_id: UUID):
        student_entity = await self._get_student_or_fail(student_id)
        return students.StudentRead.model_validate(student_entity)

    async def update_student(self, student_id: UUID, student_in: students.StudentUpdate):
        students_entity = await self._get_student_or_fail(student_id)
        update_data = student_in.model_dump(exclude_unset=True)
        if (course_id := update_data.pop("course_id", None)):
            students_entity.course_id = course_id
        for key, value in update_data.items():
            setattr(students_entity, key, value)
        updated_student = await self.students_repo.update(students_entity)
        await self.session.flush()
        await self.session.refresh(updated_student)
        return students.StudentRead.model_validate(updated_student)

    async def delete_student(self, student_id: UUID):
        students_entity = await self._get_student_or_fail(student_id)
        await self.students_repo.delete(students_entity)
        return True
