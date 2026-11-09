from src.repositories.base_repository import BaseRepository
from uuid import UUID
from sqlalchemy import update, case, select
from src.db import SessionDep
from src.models.product import ProductModel
from src.config import settings


class ProductRepository(BaseRepository[ProductModel]):
    def __init__(self, session: SessionDep):
        super().__init__(ProductModel, session)

    async def get_by_id(self, obj_id: UUID) -> ProductModel | None:
        stmt = select(ProductModel).where(ProductModel.id == obj_id, ProductModel.is_deleted == False)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def increase_stock_batch(self, quantities: dict[UUID, int]) -> None:
        if not quantities:
            return
        increments = case(quantities, value=ProductModel.id, else_=settings.stock_case_else_value)
        stmt = (
            update(ProductModel)
            .where(ProductModel.id.in_(quantities), ProductModel.is_deleted == False,)
            .values(stock=ProductModel.stock + increments))
        await self.session.execute(stmt)

    async def get_many_for_update(self, product_ids: list[UUID]) -> list[ProductModel]:
        if not product_ids:
            return []
        stmt = (
            select(ProductModel)
            .where(
                ProductModel.id.in_(product_ids), ProductModel.is_deleted == False,)
            .order_by(ProductModel.id)
            .with_for_update())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def decrease_stock_batch(self, quantities: dict[UUID, int]) -> int:
        if not quantities:
            return 0
        decrements = case(
            quantities,
            value=ProductModel.id,
            else_=0)
        stmt = (
            update(ProductModel)
            .where(
                ProductModel.id.in_(quantities), ProductModel.is_deleted == False, ProductModel.stock >= decrements)
            .values(stock=ProductModel.stock - decrements))
        result = await self.session.execute(stmt)
        return result.rowcount or 0
