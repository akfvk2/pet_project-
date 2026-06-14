import redis.asyncio as redis
import logging
from src.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self, url: str):
        self._client = redis.from_url(url, encoding="utf-8", decode_responses=True)

    async def get(self, key: str) -> str | None:
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")
            return None

    async def setex(self, key: str, ttl: int, value: str) -> None:
        try:
            await self._client.set(key, value, ex=ttl)
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")

    async def delete(self, key: str) -> None:
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")


redis_client = RedisClient(settings.redis_url)