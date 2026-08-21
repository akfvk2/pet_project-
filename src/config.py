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
    retry_jitter: float = Field(default=1.0, env="RETRY_JITTER")
    retry_status_codes: set[int] = Field(default=[408, 429, 500, 502, 503, 504], env="RETRY_STATUS_CODES")
    http_timeout: float = Field(default=5.0, env="HTTP_TIMEOUT")
    reconciliation_interval_seconds: float = Field(default=30.0, env="RECONCILIATION_INTERVAL_SECONDS")
    reconciliation_max_attempts: int = Field(default=5, env="RECONCILIATION_MAX_ATTEMPTS")
    reconciliation_stale_in_progress_seconds: int = Field(default=300, env="RECONCILIATION_STALE_IN_PROGRESS_SECONDS")
    reconciliation_unreachable_alert_attempts: int = Field(default=10, env="RECONCILIATION_UNREACHABLE_ALERT_ATTEMPTS")
    reconciliation_concurrency: int = Field(default=5, env="RECONCILIATION_CONCURRENCY")
    reconciliation_unreachable_backoff_max_seconds: float = Field(default=3600.0,env="RECONCILIATION_UNREACHABLE_BACKOFF_MAX_SECONDS")
    orders_path: str = Field(default="/v1/orders", env="ORDERS_PATH")
    reconciliation_row_processing_timeout_seconds: float = Field(default=60.0,env="RECONCILIATION_ROW_PROCESSING_TIMEOUT_SECONDS")

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

settings = Settings()