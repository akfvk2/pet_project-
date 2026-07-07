from src.repositories.base_repository import BaseRepository
from src.models.pending_order_confirmation import PendingOrderConfirmationModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class PendingOrderConfirmationRepository(BaseRepository[PendingOrderConfirmationModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(PendingOrderConfirmationModel, session)

    async def get_all_pending(self) -> list[PendingOrderConfirmationModel]:
        result = await self.session.execute(
            select(self.model).where(self.model.is_deleted == False)
        )
        return list(result.scalars().all())