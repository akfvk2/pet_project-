from datetime import datetime, timezone, timedelta
from uuid import uuid4
import pytest_asyncio
from sqlalchemy import update, delete
from src.repositories.outbox_event import OutboxEventRepository
from src.models.outbox_event import OutboxEventModel, OutboxEventStatus
from src.config import settings


@pytest_asyncio.fixture(autouse=True)
async def _clean_outbox_events(db_session):
    # тесты в этом файле делят одну и ту же таблицу между собой (db_session не изолирует БД),
    # поэтому перед каждым тестом чистим outbox_events, чтобы события из предыдущих тестов
    # не подхватывались claim_batch
    await db_session.execute(delete(OutboxEventModel))
    await db_session.commit()
    yield


@pytest_asyncio.fixture
async def repo(db_session):
    return OutboxEventRepository(db_session)


def make_event() -> OutboxEventModel:
    return OutboxEventModel(id=uuid4(), topic="t", key="k", payload="p")


class TestOutboxEventRepository:
    async def test_claim_batch_claims_pending_event(self, repo, db_session):
        event = make_event()
        repo.register_event(event)
        await db_session.commit()

        claimed = await repo.claim_batch()
        await db_session.commit()

        assert len(claimed) == 1
        assert claimed[0].id == event.id
        assert claimed[0].status == OutboxEventStatus.IN_PROGRESS

    async def test_claim_batch_skips_pending_with_future_retry_at(self, repo, db_session):
        event = make_event()
        repo.register_event(event)
        await db_session.commit()

        future = datetime.now(timezone.utc) + timedelta(minutes=10)
        await db_session.execute(
            update(OutboxEventModel).where(OutboxEventModel.id == event.id).values(next_retry_at=future)
        )
        await db_session.commit()

        claimed = await repo.claim_batch()

        assert claimed == []

    async def test_claim_batch_reclaims_stale_in_progress_and_bumps_stale_attempt(self, repo, db_session):
        event = make_event()
        repo.register_event(event)
        await db_session.commit()
        await repo.claim_batch()
        await db_session.commit()

        stale_time = datetime.now(timezone.utc) - timedelta(seconds=settings.outbox_stale_in_progress_seconds + 1)
        await db_session.execute(
            update(OutboxEventModel).where(OutboxEventModel.id == event.id).values(updated_at=stale_time)
        )
        await db_session.commit()

        reclaimed = await repo.claim_batch()
        await db_session.commit()

        assert len(reclaimed) == 1
        assert reclaimed[0].stale_attempt == 1

    async def test_mark_published_fails_on_version_mismatch(self, repo, db_session):
        event = make_event()
        repo.register_event(event)
        await db_session.commit()
        await repo.claim_batch()
        await db_session.commit()

        updated = await repo.mark_published(event.id, expected_version=999)

        assert updated is False

    async def test_mark_published_succeeds_with_correct_version(self, repo, db_session):
        event = make_event()
        repo.register_event(event)
        await db_session.commit()
        claimed = await repo.claim_batch()
        await db_session.commit()

        updated = await repo.mark_published(event.id, claimed[0].version)

        assert updated is True

    async def test_mark_failed_updates_status_attempts_and_last_error(self, repo, db_session):
        event = make_event()
        repo.register_event(event)
        await db_session.commit()
        claimed = await repo.claim_batch()
        await db_session.commit()

        retry_at = datetime.now(timezone.utc) + timedelta(seconds=30)
        updated = await repo.mark_failed(
            event.id, claimed[0].version, attempts=1,
            status=OutboxEventStatus.PENDING, next_retry_at=retry_at, last_error="boom",
        )
        await db_session.commit()

        assert updated is True
        row = await repo.get_by_id(event.id)
        assert row.status == OutboxEventStatus.PENDING
        assert row.attempts == 1
        assert row.last_error == "boom"

    async def test_fail_permanently_stuck_marks_exhausted_events_as_failed(self, repo, db_session):
        event = make_event()
        repo.register_event(event)
        await db_session.commit()
        await repo.claim_batch()
        await db_session.commit()

        stale_time = datetime.now(timezone.utc) - timedelta(seconds=settings.outbox_stale_in_progress_seconds + 1)
        await db_session.execute(
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event.id)
            .values(updated_at=stale_time, stale_attempt=settings.outbox_stale_max_attempts)
        )
        await db_session.commit()

        affected = await repo.fail_permanently_stuck()
        await db_session.commit()

        assert affected == 1
        row = await repo.get_by_id(event.id)
        assert row.status == OutboxEventStatus.FAILED
