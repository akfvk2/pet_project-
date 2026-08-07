from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.pending_order_confirmation import PendingOrderConfirmationModel


class OrderRecovery:
    def __init__(self, session: AsyncSession):
        self.session = session

    def new_reference_id(self) -> UUID:
        return uuid4()

    def register_pending(self, user_id: UUID, reference_id: UUID) -> None:
        self.session.add(PendingOrderConfirmationModel(user_id=user_id, reference_id=reference_id))

    async def resolve_pending(self, reference_id: UUID) -> None:
        result = await self.session.execute(
            select(PendingOrderConfirmationModel).where(PendingOrderConfirmationModel.reference_id == reference_id)
        )
        pending = result.scalar_one_or_none()
        if pending:
            pending.is_deleted = True