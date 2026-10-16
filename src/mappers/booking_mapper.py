from src.schemas.bookings import BookingRead, BookingCreate
from src.models.booking import BookingModel, BookingStatus





class BookingMapper:
    @staticmethod
    def to_read(booking: BookingModel) -> BookingRead:
        return BookingRead.model_validate(booking)





