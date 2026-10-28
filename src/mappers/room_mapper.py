from src.schemas.rooms import RoomRead
from src.models.room import RoomModel
from typing import Annotated
from fastapi import Depends


class RoomMapper:
    def to_read(self, room: RoomModel) -> RoomRead:
        return RoomRead.model_validate(room)

RoomMapperDep = Annotated[RoomMapper, Depends(RoomMapper)]