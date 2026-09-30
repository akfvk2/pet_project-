from src.worker.outbox_publisher import _next_status, _next_retry_at, _publish_once
from src.models.outbox_event import OutboxEventStatus, OutboxEventModel
from src.config import settings
from datetime import datetime, timezone, timedelta
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import update, delete
from testcontainers.kafka import KafkaContainer
from src.repositories.outbox_event import OutboxEventRepository
from src.db import SessionFactory
from aiokafka import AIOKafkaProducer
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class TestNextStatus:
    def test_returns_pending_below_limit(self):
        assert _next_status(settings.outbox_failed_max_attempts - 1, "event-id") == OutboxEventStatus.PENDING

    def test_returns_failed_at_limit(self):
        assert _next_status(settings.outbox_failed_max_attempts, "event-id") == OutboxEventStatus.FAILED


class TestNextRetryAt:
    def test_first_attempt_uses_base_delay(self):
        before = datetime.now(timezone.utc)
        result = _next_retry_at(1)
        delay = (result - before).total_seconds()
        assert settings.outbox_retry_base_seconds - 1 <= delay <= settings.outbox_retry_base_seconds + 1

    def test_delay_doubles_on_second_attempt(self):
        first = _next_retry_at(1)
        second = _next_retry_at(2)
        now = datetime.now(timezone.utc)
        first_delay = (first - now).total_seconds()
        second_delay = (second - now).total_seconds()
        assert second_delay > first_delay * 1.8

    def test_returns_none_at_limit(self):
        assert _next_retry_at(settings.outbox_failed_max_attempts) is None

class _ReusableSession:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(scope="session")
def kafka_container():
    with KafkaContainer() as container:
        yield container


@pytest.fixture(scope="session")
def kafka_bootstrap_servers(kafka_container):
    return kafka_container.get_bootstrap_server()


@pytest_asyncio.fixture(autouse=True)
async def _clean_outbox_events(db_session):
    await db_session.execute(delete(OutboxEventModel))
    await db_session.commit()
    yield

@pytest.fixture
def repo(db_session):
    return OutboxEventRepository(db_session)

@pytest.fixture
def session_factory(db_session):
    return lambda: _ReusableSession(db_session)

@pytest_asyncio.fixture
async def real_producer_factory(kafka_bootstrap_servers):
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers, acks="all", enable_idempotence=True)
    await producer.start()
    async def _get():
        return producer
    yield _get
    await producer.stop()


@pytest.fixture
def broken_producer_factory():
    async def _get():
        producer = AIOKafkaProducer(
            bootstrap_servers="127.0.0.1:1", acks="all", enable_idempotence=True)
        await producer.start()
        return producer
    return _get


@pytest.fixture
def fetch_persisted_event(db_url):
    async def _fetch(event_id):
        engine = create_async_engine(db_url, poolclass=NullPool)
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as verify_session:
            verify_repo = OutboxEventRepository(verify_session)
            return await verify_repo.get_by_id(event_id)
        await engine.dispose()
        return result
    return _fetch

class TestPublishOnce:
    async def test_marks_event_published_on_real_kafka_send(self, db_session, repo, session_factory, real_producer_factory, fetch_persisted_event):
        event = OutboxEventModel(id=uuid4(), topic="outbox-test-topic", key="k", payload="p")
        repo.register_event(event)
        await db_session.commit()
        had_work = await _publish_once(session_factory, real_producer_factory)
        assert had_work is True
        row = await fetch_persisted_event(event.id)
        assert row.status == OutboxEventStatus.PUBLISHED

    async def test_marks_event_failed_when_attempts_exhausted_on_unreachable_kafka(self, db_session, repo, session_factory,
                                                                                   broken_producer_factory, fetch_persisted_event):
        event = OutboxEventModel(id=uuid4(), topic="outbox-test-topic", key="k", payload="p")
        repo.register_event(event)
        await db_session.commit()
        await db_session.execute(
            update(OutboxEventModel).where(OutboxEventModel.id == event.id)
            .values(attempts=settings.outbox_failed_max_attempts - 1))
        await db_session.commit()
        had_work = await _publish_once(session_factory, broken_producer_factory)
        assert had_work is True
        row = await fetch_persisted_event(event.id)
        assert row.status == OutboxEventStatus.FAILED
        assert row.attempts == settings.outbox_failed_max_attempts
        assert row.next_retry_at is None

    async def test_marks_event_pending_with_backoff_on_unreachable_kafka(self, db_session, repo, session_factory,
                                                                        broken_producer_factory, fetch_persisted_event):
        event = OutboxEventModel(id=uuid4(), topic="outbox-test-topic", key="k", payload="p")
        repo.register_event(event)
        await db_session.commit()
        had_work = await _publish_once(session_factory, broken_producer_factory)
        assert had_work is True
        row = await fetch_persisted_event(event.id)
        assert row.status == OutboxEventStatus.PENDING
        assert row.attempts == 1
        assert row.last_error is not None
        assert row.next_retry_at is not None

    async def test_skips_event_with_future_retry_at(self, db_session, repo, session_factory, real_producer_factory):
        event = OutboxEventModel(id=uuid4(), topic="outbox-test-topic", key="k", payload="p")
        repo.register_event(event)
        await db_session.commit()
        future = datetime.now(timezone.utc) + timedelta(minutes=10)
        await db_session.execute(
            update(OutboxEventModel).where(OutboxEventModel.id == event.id).values(next_retry_at=future))
        await db_session.commit()
        had_work = await _publish_once(session_factory, real_producer_factory)
        assert had_work is False

    async def test_fails_permanently_stuck_event_without_publishing(self, db_session, repo, session_factory,
                                                                    real_producer_factory, fetch_persisted_event):
        event = OutboxEventModel(id=uuid4(), topic="outbox-test-topic", key="k", payload="p")
        repo.register_event(event)
        await db_session.commit()
        await repo.claim_batch()
        await db_session.commit()
        stale_time = datetime.now(timezone.utc) - timedelta(seconds=settings.outbox_stale_in_progress_seconds + 1)
        await db_session.execute(
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event.id)
            .values(updated_at=stale_time, stale_attempt=settings.outbox_stale_max_attempts))
        await db_session.commit()
        had_work = await _publish_once(session_factory, real_producer_factory)
        assert had_work is False
        row = await fetch_persisted_event(event.id)
        assert row.status == OutboxEventStatus.FAILED