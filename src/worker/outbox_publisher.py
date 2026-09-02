import asyncio
import logging
from aiokafka import AIOKafkaProducer
from src.db import SessionFactory
from src.config import settings
from src.repositories.outbox_event import OutboxEventRepository

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


async def close_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None


async def _publish_once() -> None:
    async with SessionFactory() as session:
        repo = OutboxEventRepository(session)
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
        except Exception:
            logger.exception(f"Outbox: failed to publish event {event.id}")
            async with SessionFactory() as session:
                repo = OutboxEventRepository(session)
                updated = await repo.mark_failed(event.id, event.version, event.attempts + 1)
                if not updated:
                    logger.warning(f"Outbox: event {event.id} was no longer at expected version, skipping")
                await session.commit()
            continue

        async with SessionFactory() as session:
            repo = OutboxEventRepository(session)
            updated = await repo.mark_published(event.id, event.version)
            if not updated:
                logger.warning(f"Outbox: event {event.id} was no longer at expected version, skipping")
            await session.commit()


async def run_outbox_publisher() -> None:
    while True:
        try:
            await _publish_once()
        except Exception:
            logger.exception("Outbox publisher iteration failed")
        await asyncio.sleep(settings.outbox_publish_interval_seconds)