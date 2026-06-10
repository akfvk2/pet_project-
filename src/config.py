import os

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env='postgres_url')
    redis_url: str = Field(default='redis://localhost:6379', env='redis_url')
    order_service_url: str = Field(default="http://localhost:8001", env="ORDER_SERVICE_URL")    
    retry_max_attempts: int = Field(default=3, env="RETRY_MAX_ATTEMPTS")
    retry_initial_wait: float = Field(default=0.5, env="RETRY_INITIAL_WAIT")
    retry_max_wait: float = Field(default=5.0, env="RETRY_MAX_WAIT")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')