import httpx
import logging
from uuid import UUID
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception
from src.config import settings
from src.exceptions.service_exception import ServiceException
from src.exceptions.retryable import RetryableException
from src.schemas.orders import OrderCreateRequest, OrderResponse, OrderCreate
from src.models.user import UserModel
from http import HTTPStatus
from typing import NoReturn


logger = logging.getLogger(__name__)



def _should_retry(exc: BaseException) -> bool:
    return isinstance(exc, RetryableException)

class OrderServiceClient:
    def __init__(self):
        self.base_url = settings.order_service_url
        self.client = httpx.AsyncClient()

    def parse_orders(self, response: httpx.Response) -> list[OrderResponse]:
        return [OrderResponse(**item) for item in response.json()]

    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential_jitter(
            initial=settings.retry_initial_wait,
            max=settings.retry_max_wait,
            jitter=settings.retry_jitter,
        ),
        retry=retry_if_exception(_should_retry),
    )
    async def get_orders_by_user_id(self, user_id: UUID) -> list[OrderResponse]:
        url = f"{self.base_url}/v1/orders/by-user/{user_id}"
        try:
            response = await self.client.get(url, timeout=settings.http_timeout)
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            raise RetryableException(HTTPStatus.SERVICE_UNAVAILABLE, str(exc)) from exc
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            if response.status_code in settings.retry_status_codes:
                raise RetryableException(response.status_code, response.text)
            raise ServiceException(response.status_code, response.text)
        return self.parse_orders(response)

    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential_jitter(
            initial=settings.retry_initial_wait,
            max=settings.retry_max_wait,
            jitter=settings.retry_jitter,
        ),
        retry=retry_if_exception(_should_retry),
    )
    async def create_order(self, user: UserModel, order_in: OrderCreate, reference_id: UUID) -> OrderResponse:
        payload = OrderCreateRequest(
            **order_in.model_dump(),
            user_id=user.id,
            reference_id=reference_id,
        )
        url = f"{self.base_url}/v1/orders/"
        try:
            response = await self.client.post(url, timeout=settings.http_timeout, json=payload.model_dump(mode="json"))
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            raise RetryableException(HTTPStatus.SERVICE_UNAVAILABLE, str(exc)) from exc
        if response.status_code >= HTTPStatus.BAD_REQUEST and response.status_code != HTTPStatus.NOT_FOUND:
            if response.status_code in settings.retry_status_codes:
                raise RetryableException(response.status_code, response.text)
            raise ServiceException(response.status_code, response.text)
        return OrderResponse(**response.json())

