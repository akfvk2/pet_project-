from src.exceptions.base import AppException


class ServiceException(AppException):
    def __init__(self, status_code: int, message: str):
        super().__init__(
            message=f"Service error {status_code}: {message}",
            status_code=status_code
        )

class NonRetryableException(ServiceException):
    pass

class NotFoundException(NonRetryableException):
    def __init__(self, message: str = "Not found"):
        super().__init__(message=message, status_code=404)


class ServiceUnavailableError(NonRetryableException):
    def __init__(self, message: str = "Service unavailable"):
        super().__init__(status_code=503, message=message)

class RetryableException(ServiceException):
    pass

class ServiceUnreachableException(RetryableException):
    pass
