from typing import Annotated
from fastapi import Depends
from src.models.order import OrderModel, OrderStatus
from src.repositories.base_repository import BaseRepository
from src.db import SessionDep
from uuid import UUID
from sqlalchemy import select, update


class OrderRepository(BaseRepository[OrderModel]):
    def __init__(self, session: SessionDep):
        super().__init__(OrderModel, session)

    async def get_by_id(self, obj_id: UUID) -> OrderModel | None:
        stmt = select(OrderModel).where(OrderModel.id == obj_id, OrderModel.is_deleted == False)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def cancel_order(self, order_id: UUID) -> bool:
        stmt = (
            update(OrderModel)
            .where(OrderModel.id == order_id, OrderModel.status == OrderStatus.PENDING, OrderModel.is_deleted == False)
            .values(status=OrderStatus.CANCELLED.value, is_deleted=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0


OrderRepositoryDep = Annotated[OrderRepository, Depends(OrderRepository)]

