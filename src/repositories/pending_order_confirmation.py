from src.repositories.base_repository import BaseRepository
from src.models.pending_order_confirmation import PendingOrderConfirmationModel
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum
from datetime import datetime, timedelta, timezone
from sqlalchemy import update, select, or_, and_
from src.config import settings
from uuid import UUID

class PendingOrderConfirmationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    NEEDS_REVIEW = "needs_review"

class PendingOrderConfirmationRepository(BaseRepository[PendingOrderConfirmationModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(PendingOrderConfirmationModel, session)

    async def claim_batch(self, batch_size: int = 20) -> list[PendingOrderConfirmationModel]:
        now = datetime.now(timezone.utc)
        stale_threshold = now - timedelta(seconds=settings.reconciliation_stale_in_progress_seconds)
        subquery = (
            select(self.model.id)
            .where(
                self.model.is_deleted == False,
                or_(
                    self.model.status == PendingOrderConfirmationStatus.PENDING,
                    and_(
                        self.model.status == PendingOrderConfirmationStatus.IN_PROGRESS,
                        self.model.updated_at < stale_threshold,
                    ),
                ),
            )
            .order_by(self.model.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        stmt = (
            update(self.model)
            .where(self.model.id.in_(subquery))
            .values(status=PendingOrderConfirmationStatus.IN_PROGRESS)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        claimed = list(result.scalars().all())
        await self.session.commit()
        return claimed

    async def save_if_in_progress(self, row_id: UUID, status: str, attempts: int, next_check_at: datetime) -> bool:
        stmt = (
            update(self.model)
            .where(self.model.id == row_id, self.model.status == PendingOrderConfirmationStatus.IN_PROGRESS)
            .values(status=status, attempts=attempts, next_check_at=next_check_at)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete_if_in_progress(self, row_id: UUID) -> bool:
        stmt = (
            update(self.model)
            .where(self.model.id == row_id, self.model.status == PendingOrderConfirmationStatus.IN_PROGRESS)
            .values(is_deleted=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0