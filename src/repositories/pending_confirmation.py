from src.repositories.base_repository import BaseRepository
from src.models.pending_confirmation import PendingConfirmationModel
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum
from datetime import datetime, timedelta, timezone
from sqlalchemy import update, select, or_, and_
from src.config import settings
from uuid import UUID

class PendingConfirmationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    NEEDS_REVIEW = "needs_review"

class PendingConfirmationRepository(BaseRepository[PendingConfirmationModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(PendingConfirmationModel, session)

    async def claim_batch(self, batch_size: int = 20) -> list[PendingConfirmationModel]:
        now = datetime.now(timezone.utc)
        stale_threshold = now - timedelta(seconds=settings.reconciliation_stale_in_progress_seconds)
        subquery = (
            select(self.model.id)
            .where(
                self.model.is_deleted == False,
                or_(
                    self.model.status == PendingConfirmationStatus.PENDING,
                    and_(
                        self.model.status == PendingConfirmationStatus.IN_PROGRESS,
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
            .values(status=PendingConfirmationStatus.IN_PROGRESS)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        claimed = list(result.scalars().all())
        return claimed

    async def save_if_in_progress(self, row_id: UUID, status: str, not_found_attempts: int, unreachable_attempts: int, next_check_at: datetime) -> bool:
        stmt = (
            update(self.model)
            .where(self.model.id == row_id, self.model.status == PendingConfirmationStatus.IN_PROGRESS)
            .values(status=status, not_found_attempts=not_found_attempts, unreachable_attempts=unreachable_attempts, next_check_at=next_check_at)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete_if_in_progress(self, row_id: UUID) -> bool:
        stmt = (
            update(self.model)
            .where(self.model.id == row_id, self.model.status == PendingConfirmationStatus.IN_PROGRESS)
            .values(is_deleted=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    def register_pending(self, user_id: UUID, reference_id: UUID) -> None:
        self.session.add(PendingConfirmationModel(user_id=user_id, reference_id=reference_id))

    async def resolve_pending(self, reference_id: UUID) -> None:
        result = await self.session.execute(
            select(PendingConfirmationModel).where(PendingConfirmationModel.reference_id == reference_id)
        )
        pending = result.scalar_one_or_none()
        if pending:
            pending.is_deleted = True