from src.exceptions.base import AppException


class BookingConflictException(AppException):
    def __init__(self, message: str = "Booking conflict"):
        super().__init__(message, 409)