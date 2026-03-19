from sqlalchemy.ext.asyncio import AsyncSession
from models.shemas import students_s
from repositories.repositories import StudentRepository
from exceptions import NotFoundException
from models import users
from models.shemas import students_s

class StudentService:
    def __init__(self, session: AsyncSession):
        self.session = session



    async def create_student(self, student_in:students_s.StudentCreate):
        students_entity = users.Students(**student_in.model_dump())
        student_repo = StudentRepository(self.session)
        db_student = await student_repo.create(students_entity)
        return await students_s.StudentRead.model_validate(db_student)


    async def get_student_by_id(self, student_id: int):
        student_repo = StudentRepository(self.session)
        student_entity = await student_repo.get_by_id(student_id)
        if not student_entity:
            raise NotFoundException("Student not found")
        return students_s.StudentRead.model_validate(student_entity)


    async def update_student(self, student_id: int, student_in: students_s.StudentUpdate):
        student_repo = StudentRepository(self.session)
        students_entity = await student_repo.get_by_id(student_id)
        if not students_entity:
            raise NotFoundException("Student not found")
        update_data = student_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(students_entity, key, value)
        update_students = await student_repo.update(students_entity)
        return students_s.StudentRead.model_validate(update_students)


    async def delete_student(self, student_id: int):
        student_repo = StudentRepository(self.session)
        students_entity = await student_repo.get_by_id(student_id)
        if not students_entity:
            raise NotFoundException("Student not found")
        await student_repo.delete(students_entity)
        return True
