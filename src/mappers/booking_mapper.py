from src.schemas.bookings import BookingRead, BookingCreate
from src.models.booking import BookingModel




class BookingMapper:
    @staticmethod
    def to_read(booking: BookingModel) -> BookingRead:
        return BookingRead.model_validate(booking)

    @staticmethod
    def to_reads(bookings: list[BookingModel]) -> list[BookingRead]:
        return [BookingRead.model_validate(b) for b in bookings]

    @staticmethod
    def to_models(bookings_in: list[BookingCreate]) -> list[BookingModel]:
        return [booking_in.to_model() for booking_in in bookings_in]

    @staticmethod
    def to_model(booking_in: BookingCreate) -> BookingModel:
        return booking_in.to_model()

