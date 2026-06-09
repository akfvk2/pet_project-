import httpx
import logging
from uuid import UUID
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from src.clients.circuit_breaker import AsyncCircuitBreaker, CircuitBreakerOpenError

logger = logging.getLogger(__name__)

ORDER_SERVICE_URL = "http://localhost:8001"

_circuit_breaker = AsyncCircuitBreaker(fail_max=3, reset_timeout=30)


class OrderServiceClient:
    def __init__(self):
        self.base_url = ORDER_SERVICE_URL

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=0.5, max=5.0, jitter=1.0),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def _fetch(self, method: str, url: str, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, timeout=5.0, **kwargs)
            response.raise_for_status()
            return response

    async def _request(self, method: str, url: str, **kwargs):
        try:
            return await _circuit_breaker.call(self._fetch, method, url, **kwargs)
        except CircuitBreakerOpenError:
            logger.warning("Circuit breaker OPEN — order service unavailable")
            return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None

    async def get_orders_by_user_id(self, user_id: UUID) -> list[dict]:
        response = await self._request("GET", f"{self.base_url}/v1/orders/by-user/{user_id}")
        if not response:
            return []
        return response.json()

    async def create_order(self, user_id: UUID, title: str, price: float, description: str = "") -> dict | None:
        response = await self._request(
            "POST",
            f"{self.base_url}/v1/orders/",
            json={"title": title, "price": price, "description": description, "user_id": str(user_id)},
        )
        if not response:
            return None
        return response.json()