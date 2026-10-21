from src.schemas.rooms import RoomRead
from src.models.room import RoomModel
from uuid import uuid4


class RoomMapper:
    @staticmethod
    def to_read(room: RoomModel) -> RoomRead:
        return RoomRead.model_validate(room)