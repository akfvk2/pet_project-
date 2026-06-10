import httpx
import logging
from uuid import UUID
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception
from src.config import Settings
from src.exceptions.order_service_error import OrderServiceException

logger = logging.getLogger(__name__)
settings = Settings()


def _should_retry(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    return isinstance(exc, (httpx.TimeoutException, httpx.ConnectError))


class OrderServiceClient:
    def __init__(self):
        self.base_url = settings.order_service_url
        self.client = httpx.AsyncClient()

    @retry(
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential_jitter(
            initial=settings.retry_initial_wait,
            max=settings.retry_max_wait,
            jitter=1.0,
        ),
        retry=retry_if_exception(_should_retry),
    )
    async def _fetch(self, method: str, url: str, **kwargs) -> httpx.Response:
        response = await self.client.request(method, url, timeout=5.0, **kwargs)
        if response.status_code >= 400:
            raise OrderServiceException(response.status_code, response.text)
        return response

    async def get_orders_by_user_id(self, user_id: UUID) -> list[dict]:
        try:
            response = await self._fetch("GET", f"{self.base_url}/v1/orders/by-user/{user_id}")
            return response.json()
        except OrderServiceException as e:
            if e.status_code == 404:
                return []
            raise

    async def create_order(self, user_id: UUID, title: str, price: float, description: str = "") -> dict:
        response = await self._fetch(
            "POST",
            f"{self.base_url}/v1/orders/",
            json={"title": title, "price": price, "description": description, "user_id": str(user_id)},
        )
        return response.json()