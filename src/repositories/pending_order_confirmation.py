from src.repositories.base_repository import BaseRepository
from src.models.pending_order_confirmation import PendingOrderConfirmationModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select


PENDING = "pending"
IN_PROGRESS = "in_progress"
NEEDS_REVIEW = "needs_review"

class PendingOrderConfirmationRepository(BaseRepository[PendingOrderConfirmationModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(PendingOrderConfirmationModel, session)

    async def claim_batch(self, batch_size: int = 20) -> list[PendingOrderConfirmationModel]:
        subquery = (
            select(self.model.id)
            .where(self.model.status == PENDING, self.model.is_deleted == False)
            .order_by(self.model.id)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        stmt = (
            update(self.model)
            .where(self.model.id.in_(subquery))
            .values(status=IN_PROGRESS)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())