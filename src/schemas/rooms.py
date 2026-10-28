from uuid import UUID, uuid4
from src.exceptions.validation_error import ValidationException
from src.models.room import RoomModel
from pydantic import BaseModel, ConfigDict, field_validator


class RoomRead(BaseModel):
    id: UUID
    roomname: str

    model_config = ConfigDict(from_attributes=True)

class RoomCreate(BaseModel):
    roomname: str



    @field_validator("roomname")
    @classmethod
    def validate_room(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValidationException(message='Room name cannot be empty')
        if len(cleaned_value) < 2:
            raise ValidationException(message='Please provide a real room name')
        return cleaned_value

    def to_model(self) -> RoomModel:
        return RoomModel(id=uuid4(), **self.model_dump())