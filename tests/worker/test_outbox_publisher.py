from src.worker.outbox_publisher import _next_status, _next_retry_at
from src.models.outbox_event import OutboxEventStatus
from src.config import settings


class TestNextStatus:
    def test_returns_pending_below_limit(self):
        assert _next_status(settings.outbox_failed_max_attempts - 1, "event-id") == OutboxEventStatus.PENDING

    def test_returns_failed_at_limit(self):
        assert _next_status(settings.outbox_failed_max_attempts, "event-id") == OutboxEventStatus.FAILED


class TestNextRetryAt:
    def test_first_attempt_uses_base_delay(self):
        from datetime import datetime, timezone
        before = datetime.now(timezone.utc)
        result = _next_retry_at(1)
        delay = (result - before).total_seconds()
        assert settings.outbox_retry_base_seconds - 1 <= delay <= settings.outbox_retry_base_seconds + 1

    def test_delay_doubles_on_second_attempt(self):
        first = _next_retry_at(1)
        second = _next_retry_at(2)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        first_delay = (first - now).total_seconds()
        second_delay = (second - now).total_seconds()
        assert second_delay > first_delay * 1.8

    def test_returns_none_at_limit(self):
        assert _next_retry_at(settings.outbox_failed_max_attempts) is None