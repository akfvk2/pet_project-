from src.repositories.base_repository import BaseRepository
from typing import Annotated
from uuid import UUID
from fastapi import Depends
from sqlalchemy import update, text, select
from src.db import SessionDep
from src.models.product import ProductModel

class ProductRepository(BaseRepository[ProductModel]):
    def __init__(self, session: SessionDep):
        super().__init__(ProductModel, session)

    async def get_by_id(self, obj_id: UUID) -> ProductModel | None:
        stmt = select(ProductModel).where(ProductModel.id == obj_id, ProductModel.is_deleted == False)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def lock_product(self, product_id: UUID) -> None:
        await self.session.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:product_id))"),
            {"product_id": str(product_id)},
        )

    async def decrease_stock(self, product_id: UUID, quantity: int) -> None:
        stmt = (
            update(ProductModel)
            .where(ProductModel.id == product_id, ProductModel.is_deleted == False)
            .values(stock=ProductModel.stock - quantity)
        )
        await self.session.execute(stmt)

    async def increase_stock(self, product_id: UUID, quantity: int) -> None:
        stmt = (
            update(ProductModel)
            .where(ProductModel.id == product_id, ProductModel.is_deleted == False)
            .values(stock=ProductModel.stock + quantity)
        )
        await self.session.execute(stmt)

ProductRepositoryDep = Annotated[ProductRepository, Depends(ProductRepository)]