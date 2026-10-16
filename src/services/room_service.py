from uuid import UUID
from src.db import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.room import RoomRepository
from src.schemas.rooms import RoomCreate, RoomRead
from src.services.service_helpers import get_by_id_or_fail
from src.mappers.room_mapper import RoomMapper

async def get_room_repository(session: AsyncSession = Depends(get_session)) -> RoomRepository:
    return RoomRepository(session)

class RoomService:
    def __init__(self, repo: RoomRepository = Depends(get_room_repository)):
        self.repo = repo

    async def create(self, room_in: RoomCreate) -> RoomRead:
        room = room_in.to_model()
        db_room = await self.repo.create(room)
        return RoomMapper.to_read(db_room)

    async def get_by_id(self, room_id: UUID) -> RoomRead:
        room = await get_by_id_or_fail(self.repo, room_id, "Room")
        return RoomMapper.to_read(room)

    async def delete(self, room_id: UUID) ->bool:
        room = await get_by_id_or_fail(self.repo, room_id, "Room")
        await self.repo.delete(room)
        return True

