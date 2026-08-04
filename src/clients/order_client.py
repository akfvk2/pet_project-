import httpx
import logging
from uuid import UUID
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception
from src.config import settings
from src.exceptions.service_exception import ServiceException
from src.exceptions.retryable import RetryableException
from src.schemas.orders import OrderCreateRequest, OrderResponse, OrderCreate
from http import HTTPStatus
from typing import NoReturn


logger = logging.getLogger(__name__)



def _should_retry(exc: BaseException) -> bool:
    return isinstance(exc, RetryableException)

class OrderServiceClient:
    def __init__(self):
        self.base_url = settings.order_service_url
        self.client = httpx.AsyncClient()

    async def close(self) -> None:
        await self.client.aclose()

    def parse_orders(self, response: httpx.Response) -> list[OrderResponse]:
        return [OrderResponse(**item) for item in response.json()]

    def _build_order_payload(self, order_in: OrderCreate, user_id: UUID, reference_id: UUID) -> OrderCreateRequest:
        return OrderCreateRequest(
            **order_in.model_dump(),
            user_id=user_id,
            reference_id=reference_id,
        )

    def parse_order(self, response: httpx.Response) -> OrderResponse:
        return OrderResponse(**response.json())

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
        url = f"{self.base_url}/v1/orders"
        try:
            response = await self.client.get(url, params={"user_id": str(user_id)}, timeout=settings.http_timeout)
        except httpx.RequestError as exc:
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
    async def create_order(self, user_id: UUID, order_in: OrderCreate, reference_id: UUID) -> OrderResponse:
        payload = self._build_order_payload(order_in, user_id, reference_id)
        url = f"{self.base_url}/v1/orders/"
        try:
            response = await self.client.post(url, timeout=settings.http_timeout, json=payload.model_dump(mode="json"))
        except httpx.RequestError as exc:
            raise RetryableException(HTTPStatus.SERVICE_UNAVAILABLE, str(exc)) from exc
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            if response.status_code in settings.retry_status_codes:
                raise RetryableException(response.status_code, response.text)
            raise ServiceException(response.status_code, response.text)
        return self.parse_order(response)

order_service_client = OrderServiceClient()
