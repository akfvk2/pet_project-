from pydantic import BaseModel, ConfigDict, model_validator
from uuid import UUID, uuid4
from src.exceptions.invalid_booking import InvalidBookingRangeException
from datetime import datetime
from src.models.booking import BookingStatus, BookingModel
from src.schemas.rooms import RoomRead
from src.schemas.users import UserBookingRead


class BookingBase(BaseModel):
    starts_at: datetime
    ends_at: datetime

class BookingCreate(BookingBase):
    room_id:UUID
    user_id:UUID


    @model_validator(mode="after")
    def validate_ends_at(self) -> "BookingCreate":
        if self.ends_at <= self.starts_at:
            raise InvalidBookingRangeException(message='End date cannot be before start date')
        return self

    def to_model(self) -> BookingModel:
        return BookingModel(id=uuid4(), status=BookingStatus.Active, **self.model_dump())

class BookingRead(BookingBase):
    id: UUID
    status: BookingStatus
    room: RoomRead
    user: UserBookingRead
    model_config = ConfigDict(from_attributes=True)

class BookingUpdate(BookingBase):
    pass


