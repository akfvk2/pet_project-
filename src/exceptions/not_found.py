from src.exceptions.base import AppException

class NotFoundException(AppException):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, 404)