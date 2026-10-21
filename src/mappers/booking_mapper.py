from src.schemas.bookings import BookingRead, BookingCreate, BookingUpdate
from src.models.booking import BookingModel, BookingStatus
from uuid import uuid4

class BookingMapper:
    @staticmethod
    def to_read(booking: BookingModel) -> BookingRead:
        return BookingRead.model_validate(booking)

    @staticmethod
    def update_model(booking_in: BookingUpdate, booking_entity: BookingModel) -> None:
        for key, value in booking_in.model_dump().items():
            setattr(booking_entity, key, value)





