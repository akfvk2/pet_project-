import httpx
import logging
from uuid import UUID
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception
from src.config import settings
from src.exceptions.external_service_exception import ExternalServiceException
from src.exceptions.retryable import RetryableException
from src.schemas.orders import OrderResponse, OrderCreate
from http import HTTPStatus
from src.mappers.order_mapper import OrderMapper


logger = logging.getLogger(__name__)



def _should_retry(exc: BaseException) -> bool:
    return isinstance(exc, RetryableException)

class OrderServiceClient:
    def __init__(self):
        self.base_url = settings.order_service_url
        self.client = httpx.AsyncClient()


    async def close(self) -> None:
        await self.client.aclose()

    def _handle_response_errors(self, response: httpx.Response) -> None:
        if response.status_code in settings.retry_status_codes:
            raise RetryableException(response.status_code, response.text)
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            raise ExternalServiceException(response.status_code, response.text)

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            return await self.client.request(method, url, timeout=settings.http_timeout, **kwargs)
        except httpx.RequestError as exc:
            raise RetryableException(HTTPStatus.SERVICE_UNAVAILABLE, str(exc)) from exc


    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential_jitter(
            initial=settings.retry_initial_wait,
            max=settings.retry_max_wait,
            jitter=settings.retry_jitter,
        ),
        retry=retry_if_exception(_should_retry),
        reraise=True,
    )
    async def get_orders_by_user_id(self, user_id: UUID) -> list[OrderResponse]:
        url = f"{self.base_url}{settings.orders_path}"
        response = await self._request("GET", url, params={"user_id": str(user_id)})
        if response.status_code == HTTPStatus.NOT_FOUND:
            return []
        self._handle_response_errors(response)
        return OrderMapper.to_orders(response.json())


    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential_jitter(
            initial=settings.retry_initial_wait,
            max=settings.retry_max_wait,
            jitter=settings.retry_jitter,
        ),
        retry=retry_if_exception(_should_retry),
        reraise=True,
    )
    async def create_order(self, user_id: UUID, order_in: OrderCreate, reference_id: UUID) -> OrderResponse:
        payload = OrderMapper.to_create_request(order_in, user_id, reference_id)
        url = f"{self.base_url}{settings.orders_path}"
        response = await self._request("POST", url, json=payload.model_dump())
        self._handle_response_errors(response)
        return OrderMapper.to_order(response.json())

_order_service_client: OrderServiceClient | None = None

def get_order_client() -> OrderServiceClient:
    global _order_service_client
    if _order_service_client is None:
        _order_service_client = OrderServiceClient()
    return _order_service_client