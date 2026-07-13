from src.exceptions.non_retryable import NonRetryableException

class ServiceUnavailableError(NonRetryableException):
    def __init__(self, message: str = "Service unavailable"):
        super().__init__(status_code=503, message=message)