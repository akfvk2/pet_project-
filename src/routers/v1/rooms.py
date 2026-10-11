from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_session
from src.schemas import rooms
from src.services.room_service import RoomService
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=rooms.RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(room_in: rooms.RoomCreate, session: AsyncSession = Depends(get_session)):
    return await RoomService(session).create(room_in)

@router.get("/{room_id}", response_model=rooms.RoomRead)
async def get_room(room_id: UUID, session: AsyncSession = Depends(get_session)):
    return await RoomService(session).get_by_id(room_id)

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: UUID, session: AsyncSession = Depends(get_session)):
    return await RoomService(session).delete(room_id)