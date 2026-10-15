from src.exceptions.base import AppException
from fastapi import status

class ConflictException(AppException):
    def __init__(self, message: str = "Сonflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)