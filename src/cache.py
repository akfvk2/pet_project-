import redis.asyncio as redis
from src.config import Settings

settings = Settings()

redis_client: redis.Redis = redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)