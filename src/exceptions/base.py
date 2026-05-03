from typing import Any, Optional
from fastapi import Request
from fastapi.responses import UJSONResponse
from pydantic import BaseModel



class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400, extra: Any = None):
        self.message = message
        self.status_code = status_code
        self.extra = extra


class ErrorException(BaseModel):
    message: str
    extra: Optional[Any] = None
    path: str



async def app_exception_handler(request: Request, exc: AppException):
    error_data = ErrorException(
        message=exc.message,
        extra=exc.extra,
        path=request.url.path,
    )
    return UJSONResponse(
        status_code=exc.status_code,
        content=error_data.model_dump(),
    )