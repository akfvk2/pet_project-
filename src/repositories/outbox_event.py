from src.repositories.base_repository import BaseRepository
from src.models.outbox_event import OutboxEventModel, OutboxEventStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, or_, and_, case
from datetime import datetime, timedelta, timezone
from uuid import UUID
from src.config import settings



class OutboxEventRepository(BaseRepository[OutboxEventModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(OutboxEventModel, session)

    async def claim_batch(self, batch_size: int = 20) -> list[OutboxEventModel]:
        now = datetime.now(timezone.utc)
        stale_threshold = now - timedelta(seconds=settings.outbox_stale_in_progress_seconds)
        subquery = (select(self.model.id).where(
                self.model.is_deleted == False,
            or_(
                and_(
                    self.model.status == OutboxEventStatus.PENDING,
                    or_(self.model.next_retry_at.is_(None), self.model.next_retry_at <= now),
                ),
                and_(
                    self.model.status == OutboxEventStatus.IN_PROGRESS,
                    self.model.updated_at < stale_threshold,)))
            .order_by(self.model.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True))
        stmt = (
            update(self.model)
            .where(self.model.id.in_(subquery))
            .values(status=OutboxEventStatus.IN_PROGRESS, version=self.model.version + 1, updated_at=now,stale_attempt=case(
                (self.model.status == OutboxEventStatus.IN_PROGRESS, self.model.stale_attempt + 1),
                else_=self.model.stale_attempt,
            ),)
            .returning(self.model))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_published(self, event_id: UUID, expected_version: int) -> bool:
        stmt = (update(self.model).where(
                self.model.id == event_id,
                self.model.status == OutboxEventStatus.IN_PROGRESS,
                self.model.version == expected_version,
            )
            .values(status=OutboxEventStatus.PUBLISHED, version=self.model.version + 1))
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def mark_failed(self, event_id: UUID, expected_version: int, attempts: int, status:OutboxEventStatus, next_retry_at: datetime | None,
                          last_error: str | None ) -> bool:
        stmt = (update(self.model).where(
                self.model.id == event_id,
                self.model.status == OutboxEventStatus.IN_PROGRESS,
                self.model.version == expected_version,).values(
            status=status,
            attempts=attempts,
            version=self.model.version + 1,
            next_retry_at=next_retry_at,
            last_error=last_error))
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    def register_event(self, event: OutboxEventModel) -> None:
        self.session.add(event)

    async def fail_permanently_stuck(self) -> int:
        now = datetime.now(timezone.utc)
        stale_threshold = now - timedelta(seconds=settings.outbox_stale_in_progress_seconds)
        stmt = (
            update(self.model)
            .where(
                self.model.status == OutboxEventStatus.IN_PROGRESS,
                self.model.updated_at < stale_threshold,
                self.model.stale_attempt >= settings.outbox_stale_max_attempts,
            )
            .values(status=OutboxEventStatus.FAILED)
        )
        result = await self.session.execute(stmt)
        return result.rowcount