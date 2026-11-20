from uuid import UUID
from src.dependencies.products import ProductRepositoryDep
from src.exceptions.insufficient import InsufficientException
from src.exceptions.not_found import NotFoundException
from src.models.order_item import OrderItemModel
from src.models.product import ProductModel
from src.schemas.order_items import OrderItemCreate


class OrderInventoryService:
    def __init__(self, product_repo: ProductRepositoryDep):
        self.product_repo = product_repo

    async def reserve_stock(self, items: list[OrderItemCreate]) -> dict[UUID, ProductModel]:
        quantities = self._aggregate_quantities(items)
        products_by_id = await self._get_products_for_update(quantities)
        self._validate_stock(quantities, products_by_id)
        await self._decrease_stock(quantities)
        return products_by_id

    @staticmethod
    def _aggregate_quantities(items: list[OrderItemCreate]) -> dict[UUID, int]:
        quantities: dict[UUID, int] = {}
        for item in items:
            quantities[item.product_id] = (
                    quantities.get(item.product_id, 0) + item.quantity)
        return quantities

    async def _get_products_for_update(self, quantities: dict[UUID, int]) -> dict[UUID, ProductModel]:
        products = await self.product_repo.get_many_for_update(list(quantities))
        products_by_id = {product.id: product for product in products}
        missing_ids = set(quantities).difference(products_by_id)
        if missing_ids:
            product_id = sorted(missing_ids)[0]
            raise NotFoundException(f"Product {product_id} not found")
        return products_by_id

    @staticmethod
    def _validate_stock(quantities: dict[UUID, int], products_by_id: dict[UUID, ProductModel]) -> None:
        for product_id, quantity in quantities.items():
            product = products_by_id[product_id]
            if product.stock < quantity:
                raise InsufficientException(f"Not enough stock for product {product_id}")

    async def _decrease_stock(self, quantities: dict[UUID, int]) -> None:
        updated_count = await self.product_repo.decrease_stock_batch(quantities)
        if updated_count != len(quantities):
            raise InsufficientException("Could not reserve stock for all products")


    async def restore_stock(self, items: list[OrderItemModel]) -> None:
        quantities: dict[UUID, int] = {}
        for item in items:
            quantities[item.product_id] = (quantities.get(item.product_id, 0) + item.quantity)
        update_count = await self.product_repo.increase_stock_batch(quantities)
        if update_count != len(quantities):
            raise InsufficientException("Could not restore stock for all products")