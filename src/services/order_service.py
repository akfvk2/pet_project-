from uuid import UUID, uuid4
from src.repositories.order import OrderRepositoryDep
from src.repositories.product import ProductRepositoryDep
from src.mappers.warehouse_order_mapper import OrderMapperDep
from src.schemas.warehouse_orders import OrderCreate, OrderRead
from src.models.order import OrderModel
from src.models.order_item import OrderItemModel
from src.exceptions.insufficient import InsufficientException
from src.exceptions.not_found import NotFoundException
from src.services.service_helpers import get_by_id_or_fail


class OrderService:
    def __init__(self, order_repo: OrderRepositoryDep, product_repo: ProductRepositoryDep, mapper: OrderMapperDep):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.mapper = mapper


    async def create_order(self, order_in: OrderCreate) -> OrderRead:
        product_quantities: dict[UUID, int] = {}
        for item_in in order_in.items:
            product_quantities[item_in.product_id] = product_quantities.get(item_in.product_id, 0) + item_in.quantity

        for product_id in sorted(product_quantities):
            await self.product_repo.lock_product(product_id)

        items = []
        for product_id, quantity in product_quantities.items():
            product = await get_by_id_or_fail(self.product_repo, product_id, "Product")
            if product.stock < quantity:
                raise InsufficientException(f"Not enough stock for product {product.id}")

        for item_in in order_in.items:
            product = await get_by_id_or_fail(self.product_repo, item_in.product_id, "Product")
            await self.product_repo.decrease_stock(item_in.product_id, item_in.quantity)
            items.append(OrderItemModel(id=uuid4(), product_id=item_in.product_id, quantity=item_in.quantity, price=product.price))
        order = OrderModel(id=uuid4(), items=items)
        created_order = await self.order_repo.create(order)
        return self.mapper.to_read(created_order)

    async def cancel_order(self, order_id: UUID) -> bool:
        order = await get_by_id_or_fail(self.order_repo, order_id, "Order")
        cancelled = await self.order_repo.cancel_order(order_id)
        if not cancelled:
            raise NotFoundException(f"Order {order_id} not found")
        for item in order.items:
            await self.product_repo.increase_stock(item.product_id, item.quantity)
        return True

    async def get_by_id(self, order_id: UUID) -> OrderRead:
        order = await get_by_id_or_fail(self.order_repo, order_id, "Order")
        return self.mapper.to_read(order)