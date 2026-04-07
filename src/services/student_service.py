from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.repositories import StudentRepository
from src.exceptions.common import NotFoundException
from src.models import users
from src.models.schemas import students
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

class StudentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.students_repo = StudentRepository(self.session)



    async def create_student(self, student_in:students.StudentCreate):
        students_entity = users.Students(**student_in.model_dump())
        db_student = await self.students_repo.create(students_entity)
        return await students.StudentRead.model_validate(db_student)


    async def get_student_by_id(self, student_id: uuid4()):
        student_entity = await self.students_repo.get_by_id(student_id)
        if not student_entity:
            logger.error(
                f"Entity 'Student' with id {student_id} not found",
                extra={"student_id": student_id}
            )
            raise NotFoundException("Student not found")
        return students.StudentRead.model_validate(student_entity)


    async def update_student(self, student_id: uuid4(), student_in: students.StudentUpdate):
        students_entity = await self.students_repo.get_by_id(student_id)
        if not students_entity:
            logger.error(
                f"Entity 'Student' with id {student_id} not found",
                extra={"student_id": student_id}
            )
            raise NotFoundException("Student not found")
        update_data = student_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(students_entity, key, value)
        update_students = await self.students_repo.update(students_entity)
        return students.StudentRead.model_validate(update_students)


    async def delete_student(self, student_id: uuid4()):
        students_entity = await self.students_repo.get_by_id(student_id)
        if not students_entity:
            logger.error(
                f"Entity 'Student' with id {student_id} not found",
                extra={"student_id": student_id}
            )
            raise NotFoundException("Student not found")
        await self.students_repo.delete(students_entity)
        return True
