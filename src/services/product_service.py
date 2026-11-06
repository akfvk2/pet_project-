from uuid import UUID
from src.repositories.product import ProductRepositoryDep
from src.schemas.products import ProductCreate, ProductRead, ProductUpdate
from src.services.service_helpers import get_by_id_or_fail
from src.mappers.product_mapper import ProductMapperDep



class ProductService:
    def __init__ (self, repo: ProductRepositoryDep, mapper: ProductMapperDep):
        self.repo = repo
        self.mapper = mapper

    async def create(self, product_in: ProductCreate) -> ProductRead:
        product = product_in.to_model()
        db_product = await self.repo.create(product)
        return self.mapper.to_read(db_product)

    async def get_by_id(self, product_id: UUID) -> ProductRead:
        product = await get_by_id_or_fail(self.repo, product_id, "Product")
        return self.mapper.to_read(product)

    async def update(self, product_id: UUID, product_in: ProductUpdate) -> ProductRead:
        product_entity = await get_by_id_or_fail(self.repo, product_id, "Product")
        product = product_in.update_model(product_entity)
        updated_product = await self.repo.update(product)
        return self.mapper.to_read(updated_product)

    async def delete(self, product_id: UUID) -> bool:
        product = await get_by_id_or_fail(self.repo, product_id, "Product")
        await self.repo.delete(product)
        return True