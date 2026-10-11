from src.schemas.bookings import BookingRead
from src.models.booking import BookingModel




class BookingMapper:
    @staticmethod
    def to_read(booking: BookingModel) -> BookingRead:
        return BookingRead.model_validate(booking)

    @staticmethod
    def to_reads(bookings: list[BookingModel]) -> list[BookingRead]:
        return [BookingRead.model_validate(b) for b in bookings]

