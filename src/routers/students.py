
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from models import schemas
from services import StudentService


router = APIRouter()

@router.post("/", response_model=schemas.StudentRead)
async def create_student(student_in: schemas.StudentCreate, session: AsyncSession = Depends(get_session)):
    student = await StudentService.create_student(session, student_in)
    return student



@router.get("/{student_id}", response_model=schemas.StudentRead)
async def read_student(student_id: int, session: AsyncSession = Depends(get_session)):
    student = await StudentService.get_student_by_id(session, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student



@router.put("/{student_id}", response_model=schemas.StudentRead)
async def update_student(student_id: int, student_in: schemas.StudentUpdate, session: AsyncSession = Depends(get_session)):
    student = await StudentService.update_student(session, student_id, student_in)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student



@router.delete("/{student_id}")
async def delete_student(student_id: int, session: AsyncSession = Depends(get_session)):
    success = await StudentService.delete_student(session, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"ok": True}
