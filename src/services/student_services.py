from sqlalchemy.ext.asyncio import AsyncSession

from models import schemas
from repositories.repositories import StudentRepository


class StudentService:
    @staticmethod
    async def create_student(session: AsyncSession, student_in: schemas.StudentCreate):
        return await StudentRepository.create(session, student_in)

    @staticmethod
    async def get_student_by_id(session: AsyncSession, student_id: int):
        return await StudentRepository.get_by_id(session, student_id)

    @staticmethod
    async def update_student(session: AsyncSession, student_id: int, student_in: schemas.StudentUpdate):
        return await StudentRepository.update(session, student_id, student_in)

    @staticmethod
    async def delete_student(session: AsyncSession, student_id: int):
        return await StudentRepository.delete(session, student_id)
