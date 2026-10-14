from src.exceptions.base import AppException
from fastapi import status


class InvalidBookingRangeException(AppException):
    def __init__(self, message: str = "Invalid booking range"):
        super().__init__(message, 400)