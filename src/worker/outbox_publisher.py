import asyncio
import logging
from datetime import datetime, timezone, timedelta
from aiokafka import AIOKafkaProducer
from src.db import SessionFactory
from src.config import settings
from src.repositories.outbox_event import OutboxEventRepository
from src.models.outbox_event import OutboxEventStatus
from aiokafka.errors import KafkaError


logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None


async def _get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            acks="all",
            enable_idempotence=True,
        )
        await _producer.start()
    return _producer

def _next_status(attempts: int, event_id) -> OutboxEventStatus:
    if attempts >= settings.outbox_failed_max_attempts:
        logger.error(f"Outbox: event {event_id} failed permanently after {attempts} attempts")
        return OutboxEventStatus.FAILED
    return OutboxEventStatus.PENDING

def _next_retry_at(attempts: int) -> datetime | None:
    if attempts >= settings.outbox_failed_max_attempts:
        return None
    delay_seconds = min(
        settings.outbox_retry_base_seconds * (2 ** (attempts - 1)),
        settings.outbox_retry_max_seconds,
    )
    return datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)


async def close_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None


async def _publish_once() -> None:
    async with SessionFactory() as session:
        repo = OutboxEventRepository(session)
        await repo.fail_permanently_stuck()
        claimed = await repo.claim_batch()
        await session.commit()
    producer = await _get_producer()
    for event in claimed:
        try:
            await producer.send_and_wait(
                event.topic,
                key=event.key.encode("utf-8"),
                value=event.payload.encode("utf-8"),
            )
        except KafkaError as exc:
            logger.exception(f"Outbox: failed to publish event {event.id}")
            new_attempts = event.attempts + 1
            new_status = _next_status(new_attempts, event.id)
            next_retry_at = _next_retry_at(new_attempts)
            async with SessionFactory() as session:
                repo = OutboxEventRepository(session)
                updated = await repo.mark_failed(event.id, event.version, new_attempts, new_status, next_retry_at, str(exc))
                if not updated:
                    current = await repo.get_by_id(event.id)
                    actual_state = f"status={current.status}, version={current.version}" if current else "record not found"
                    logger.error(
                        f"Outbox: event {event.id} version mismatch on mark_failed — "
                        f"expected_version={event.version}, actual=({actual_state}) — "
                        f"possible concurrent processing by another worker"
                    )
                await session.commit()
            continue

        async with SessionFactory() as session:
            repo = OutboxEventRepository(session)
            updated = await repo.mark_published(event.id, event.version)
            if not updated:
                current = await repo.get_by_id(event.id)
                actual_state = f"status={current.status}, version={current.version}" if current else "record not found"
                logger.error(
                    f"Outbox: event {event.id} version mismatch on mark_published — "
                    f"expected_version={event.version}, actual=({actual_state}) — "
                    f"possible concurrent processing by another worker"
                )
            await session.commit()


async def run_outbox_publisher(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            await _publish_once()
        except Exception:
            logger.exception("Outbox publisher iteration failed")
        await asyncio.sleep(settings.outbox_publish_interval_seconds)