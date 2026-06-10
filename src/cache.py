import redis.asyncio as redis
from src.config import Settings

settings = Settings()


class RedisClient:
    def __init__(self, url: str):
        self._client = redis.from_url(url, encoding="utf-8", decode_responses=True)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        await self._client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)


redis_client = RedisClient(settings.redis_url)
