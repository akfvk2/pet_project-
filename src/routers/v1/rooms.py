from fastapi import APIRouter, status
from src.schemas import rooms
from src.services.room_service import RoomService
from uuid import UUID
from fastapi import Depends
from typing import Annotated

router = APIRouter()

RoomServiceDep = Annotated[RoomService, Depends(RoomService)]

@router.post("/", response_model=rooms.RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(room_in: rooms.RoomCreate, service: RoomServiceDep):
    return await service.create(room_in)

@router.get("/{room_id}", response_model=rooms.RoomRead)
async def get_room(room_id: UUID, service: RoomServiceDep):
    return await service.get_by_id(room_id)

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: UUID, service: RoomServiceDep):
    return await service.delete(room_id)