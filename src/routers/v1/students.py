from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.models.schemas import students
from src.services.student_service import StudentService


router = APIRouter()

@router.post("/", response_model=students.StudentRead, status_code=status.HTTP_201_CREATED)
async def create_student(student_in: students.StudentCreate, session: AsyncSession = Depends(get_session)):
    return await StudentService.create_student(session, student_in)



@router.get("/{student_id}", response_model=students.StudentRead)
async def read_student(student_id: int, session: AsyncSession = Depends(get_session)):
     return await StudentService.get_student_by_id(session, student_id)




@router.put("/{student_id}", response_model=students.StudentRead)
async def update_student(student_id: int, student_in: students.StudentUpdate, session: AsyncSession = Depends(get_session)):
    return await StudentService.update_student(session, student_id, student_in)




@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_id: int, session: AsyncSession = Depends(get_session)):
    await StudentService.delete_student(session, student_id)