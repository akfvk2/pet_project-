from src.exceptions.base import AppException
from fastapi import status

class NotFoundException(AppException):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)