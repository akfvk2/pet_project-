from uuid import UUID
from src.dependencies import ProductRepositoryDep
from src.exceptions.insufficient import InsufficientException
from src.exceptions.not_found import NotFoundException
from src.models.order_item import OrderItemModel
from src.models.product import ProductModel
from src.schemas.order_items import OrderItemCreate


class OrderInventoryService:
    def __init__(self, product_repo: ProductRepositoryDep):
        self.product_repo = product_repo

    async def reserve_stock(self, items: list[OrderItemCreate]) -> dict[UUID, ProductModel]:
        quantities: dict[UUID, int] = {}
        for item in items:
            quantities[item.product_id] = (
                quantities.get(item.product_id, 0) + item.quantity)
        products = await self.product_repo.get_many_for_update(list(quantities))
        products_by_id = {product.id: product for product in products}
        missing_ids = set(quantities).difference(products_by_id)
        if missing_ids:
            product_id = sorted(missing_ids)[0]
            raise NotFoundException(f"Product {product_id} not found")
        for product_id, quantity in quantities.items():
            product = products_by_id[product_id]
            if product.stock < quantity:
                raise InsufficientException(
                    f"Not enough stock for product {product_id}")
        updated_count = await self.product_repo.decrease_stock_batch(quantities)
        if updated_count != len(quantities):
            raise InsufficientException("Could not reserve stock for all products")
        return products_by_id

    async def restore_stock(self, items: list[OrderItemModel]) -> None:
        quantities: dict[UUID, int] = {}
        for item in items:
            quantities[item.product_id] = (quantities.get(item.product_id, 0) + item.quantity)
        await self.product_repo.increase_stock_batch(quantities)