from src.exceptions.service_exception import ServiceException

class NonRetryableException(ServiceException):
    pass