from src.exceptions.base import AppException


class ServiceException(AppException):
    def __init__(self, status_code: int, message: str):
        super().__init__(
            message=f"Service error {status_code}: {message}",
            status_code=status_code
        )