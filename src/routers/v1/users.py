from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession


from src.db import get_session
from src.models.shemas import users_s
from src.services.user_services import UserService

router = APIRouter()


@router.post("/", response_model=users_s.UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: users_s.UserCreate, session: AsyncSession = Depends(get_session)):
    user = await UserService.create_user(session, user_in)
    return user


@router.get("/{user_id}", response_model=users_s.UserRead, status_code=status.HTTP_200_OK)
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    return await UserService.get_user_by_id(session, user_id)



@router.put("/{user_id}", response_model=users_s.UserRead, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_in: users_s.UserUpdate, session: AsyncSession = Depends(get_session)):
    return await UserService.update_user(session, user_id, user_in)



@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    await UserService.delete_user(session, user_id)
