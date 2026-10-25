from uuid import UUID
from fastapi import Depends
from src.repositories.room import RoomRepositoryDep
from src.schemas.rooms import RoomCreate, RoomRead
from src.services.service_helpers import get_by_id_or_fail
from src.mappers.room_mapper import RoomMapperDep
from typing import Annotated



class RoomService:
    def __init__(self, repo: RoomRepositoryDep, mapper: RoomMapperDep):
        self.repo = repo
        self.mapper = mapper

    async def create(self, room_in: RoomCreate) -> RoomRead:
        room = room_in.to_model()
        db_room = await self.repo.create(room)
        return self.mapper.to_read(db_room)

    async def get_by_id(self, room_id: UUID) -> RoomRead:
        room = await get_by_id_or_fail(self.repo, room_id, "Room")
        return self.mapper.to_read(room)

    async def delete(self, room_id: UUID) ->bool:
        room = await get_by_id_or_fail(self.repo, room_id, "Room")
        await self.repo.delete(room)
        return True

RoomServiceDep = Annotated[RoomService, Depends(RoomService)]