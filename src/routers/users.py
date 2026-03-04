
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from db import get_session
from models import schemas
from services import UserService

router = APIRouter()


@router.post("/", response_model=schemas.UserRead)
async def create_user(user_in: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    user = await UserService.create_user(session, user_in)
    return user




@router.get("/{user_id}", response_model=schemas.UserRead)
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await UserService.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.put("/{user_id}", response_model=schemas.UserRead)
async def update_user(user_id: int, user_in: schemas.UserUpdate, session: AsyncSession = Depends(get_session)):
    user = await UserService.update_user(session, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.delete("/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    success = await UserService.delete_user(session, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}