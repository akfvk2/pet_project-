from sqlalchemy import select
from src.services.outbox_service import OutboxService
from src.repositories.outbox_event import OutboxEventRepository
from src.models.outbox_event import OutboxEventModel


async def test_register_creates_outbox_row(db_session):
    service = OutboxService(OutboxEventRepository(db_session))

    service.register(topic="my-topic", key="my-key", payload='{"a": 1}')
    await db_session.commit()

    result = await db_session.execute(select(OutboxEventModel).where(OutboxEventModel.topic == "my-topic"))
    row = result.scalar_one()
    assert row.key == "my-key"
    assert row.payload == '{"a": 1}'