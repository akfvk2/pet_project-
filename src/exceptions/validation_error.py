from src.exceptions.base import AppException


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, 422)