from src.exceptions.base import AppException
from fastapi import status


class InvalidBookingRangeError(AppException):
    def __init__(self, message: str = "Invalid booking range"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)