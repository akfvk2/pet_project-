from src.exceptions.base import AppException


class OrderServiceException(AppException):
    def __init__(self, status_code: int, message: str):
        super().__init__(
            message=f"OrderService error {status_code}: {message}",
            status_code=status_code
        )

class OrderNotFoundException(AppException):
    def __init__(self, message: str = "Order not found"):
        super().__init__(message=message, status_code=404)


class OrderServiceUnavailableError(AppException):
    def __init__(self, message: str = "Order service unavailable"):
        super().__init__(message=message, status_code=503)