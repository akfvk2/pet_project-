from src.exceptions.base import AppException
from fastapi import status


class InsufficientException(AppException):
    def __init__(self, message: str = "Insufficient"):
        super().__init__(message, status.HTTP_409_CONFLICT)