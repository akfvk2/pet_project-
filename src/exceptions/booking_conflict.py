from src.exceptions.base import AppException
from fastapi import status

class BookingConflictError(AppException):
    def __init__(self, message: str = "Booking conflicts with an existing reservation"):
        super().__init__(message, status.HTTP_409_CONFLICT)