from src.repositories.base_repository import BaseRepository
from src.models.outbox_event import OutboxEventModel, OutboxEventStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, or_, and_
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
                    self.model.status == OutboxEventStatus.PENDING,
                    and_(
                        self.model.status == OutboxEventStatus.IN_PROGRESS,
                        self.model.updated_at < stale_threshold)))
            .order_by(self.model.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True))
        stmt = (
            update(self.model)
            .where(self.model.id.in_(subquery))
            .values(status=OutboxEventStatus.IN_PROGRESS, version=self.model.version + 1)
            .returning(self.model))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_published(self, event_id: UUID, expected_version: int) -> bool:
        stmt = (update(self.model).where(
                self.model.id == event_id,
                self.model.status == OutboxEventStatus.IN_PROGRESS,
                self.model.version == expected_version,
            )
            .values(is_deleted=True, status=OutboxEventStatus.PUBLISHED))
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def mark_failed(self, event_id: UUID, expected_version: int, attempts: int) -> bool:
        stmt = (update(self.model).where(
                self.model.id == event_id,
                self.model.status == OutboxEventStatus.IN_PROGRESS,
                self.model.version == expected_version,).values(status=OutboxEventStatus.PENDING, attempts=attempts))
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    def register_event(self, event_id: UUID, topic: str, key: str, payload: str) -> None:
        self.session.add(OutboxEventModel(id=event_id, topic=topic, key=key, payload=payload))