from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_session
from schemas import users
from src.services.user_service import UserService
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=users.UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: users.UserCreate, session: AsyncSession = Depends(get_session)):
    return await UserService(session).create_user(user_in)


@router.get("/{user_id}", response_model=users.UserRead)
async def read_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    return await UserService(session).get_user_by_id(user_id)


@router.put("/{user_id}", response_model=users.UserRead)
async def update_user(user_id: UUID, user_in: users.UserUpdate, session: AsyncSession = Depends(get_session)):
    return await UserService(session).update_user(user_id, user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    await UserService(session).delete_user(user_id)
