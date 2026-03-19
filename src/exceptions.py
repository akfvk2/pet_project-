from typing import Any


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400, extra: Any = None):
        self.message = message
        self.status_code = status_code
        self.extra = extra


class NotFoundException(AppException):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, 404)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, 422)
