from src.schemas.bookings import BookingRead, BookingUpdate
from src.models.booking import BookingModel
from typing import Annotated
from fastapi import Depends

class BookingMapper:
    def to_read(self, booking: BookingModel) -> BookingRead:
        return BookingRead.model_validate(booking)

    def update_model(self, booking_in: BookingUpdate, booking_entity: BookingModel) -> BookingModel:
        for key, value in booking_in.model_dump().items():
            setattr(booking_entity, key, value)
        return booking_entity

BookingMapperDep = Annotated[BookingMapper, Depends(BookingMapper)]