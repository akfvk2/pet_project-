from src.exceptions.base import AppException
from fastapi import status

class AlreadyExistsException(AppException):
    def __init__(self, message: str = "Already exists"):
        super().__init__(message, status.HTTP_409_CONFLICT)