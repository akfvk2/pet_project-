import httpx
import logging
from uuid import UUID
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception
from src.config import settings
from src.exceptions.order_service_error import OrderServiceException, OrderNotFoundException, OrderServiceUnavailableError, RetryableOrderServiceException
from src.schemas.orders import OrderCreateRequest, OrderResponse, OrderCreate
from src.models.user import UserModel
from http import HTTPStatus

logger = logging.getLogger(__name__)



def _should_retry(exc: BaseException) -> bool:
    return isinstance(exc, RetryableOrderServiceException)

class OrderServiceClient:
    def __init__(self):
        self.base_url = settings.order_service_url
        self.client = httpx.AsyncClient()

    def _handle_errors(self, url: str, response: httpx.Response) -> None:
        if response.status_code == HTTPStatus.NOT_FOUND:
            logger.warning(f"Not found: {url}")
            raise OrderNotFoundException(response.text)
        if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            logger.error(f"Validation error {response.status_code}: {url} {response.text}")
            raise OrderServiceException(response.status_code, response.text)
        if response.status_code in settings.retry_status_codes:
            logger.error(f"Retryable error {response.status_code}: {url} {response.text}")
            raise RetryableOrderServiceException(response.status_code, response.text)
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            logger.error(f"Client error {response.status_code}: {url} {response.text}")
            raise OrderServiceException(response.status_code, response.text)

    def _handle_post_errors(self, url: str, response: httpx.Response) -> None:
        if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            logger.error(f"Validation error {response.status_code}: {url} {response.text}")
            raise OrderServiceException(response.status_code, response.text)
        if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.error(f"Service unavailable {response.status_code}: {url} {response.text}")
            raise OrderServiceUnavailableError(response.text)
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            logger.error(f"Client error {response.status_code}: {url} {response.text}")
            raise OrderServiceException(response.status_code, response.text)

    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential_jitter(
            initial=settings.retry_initial_wait,
            max=settings.retry_max_wait,
            jitter=settings.retry_jitter,
        ),
        retry=retry_if_exception(_should_retry),
    )
    async def _get(self, url: str, **kwargs) -> httpx.Response:
        response = await self.client.get(url, timeout=settings.http_timeout, **kwargs)
        self._handle_errors(url, response)
        return response

    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential_jitter(
            initial=settings.retry_initial_wait,
            max=settings.retry_max_wait,
            jitter=settings.retry_jitter,
        ),
        retry=retry_if_exception(_should_retry),
    )
    async def _post(self, url: str, **kwargs) -> httpx.Response:
        response = await self.client.post(url, timeout=5.0, **kwargs)
        self._handle_post_errors(url, response)
        return response


    async def get_orders_by_user_id(self, user_id: UUID) -> list[OrderResponse]:
        response = await self._get(f"{self.base_url}/v1/orders/by-user/{user_id}")
        return [OrderResponse(**item) for item in response.json()]


    async def create_order(self, user: UserModel, order_in: OrderCreate) -> OrderResponse:
        payload = OrderCreateRequest(
            **order_in.model_dump(),
            user_id=user.id
        )
        response = await self._post(
            f"{self.base_url}/v1/orders/",
            json=payload.model_dump(mode="json"),
        )
        return OrderResponse(**response.json())