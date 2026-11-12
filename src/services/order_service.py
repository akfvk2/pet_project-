from uuid import UUID, uuid4
from src.dependencies.orders import OrderRepositoryDep
from src.dependencies.orders import OrderMapperDep
from src.schemas.warehouse_orders import OrderCreate, OrderRead
from src.models.order import OrderModel, OrderStatus
from src.models.order_item import OrderItemModel
from src.exceptions.not_found import NotFoundException
from src.services.service_helpers import get_by_id_or_fail
from src.exceptions.already_exists import AlreadyExistsException
from src.dependencies.order_inventory import OrderInventoryServiceDep


class OrderService:
    def __init__(self, order_repo: OrderRepositoryDep, inventory_service:OrderInventoryServiceDep, mapper: OrderMapperDep,):
        self.order_repo = order_repo
        self.inventory_service = inventory_service
        self.mapper = mapper

    async def create_order(self, order_in: OrderCreate) -> OrderRead:
        products_by_id = await self.inventory_service.reserve_stock(order_in.items)
        items = [OrderItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=products_by_id[item.product_id].price)
        for item in order_in.items]
        order = OrderModel(id=uuid4(), items=items)
        created_order = await self.order_repo.create(order)
        return self.mapper.to_read(created_order)

    async def cancel_order(self, order_id: UUID) -> bool:
        order = await get_by_id_or_fail(self.order_repo, order_id, "Order")
        if order.status == OrderStatus.CANCELLED:
            raise AlreadyExistsException("Order is already cancelled")
        cancelled = await self.order_repo.cancel_order(order_id)
        if not cancelled:
            raise NotFoundException(f"Order {order_id} not found")
        await self.inventory_service.restore_stock(order.items)
        return True

    async def get_by_id(self, order_id: UUID) -> OrderRead:
        order = await get_by_id_or_fail(self.order_repo, order_id, "Order")
        return self.mapper.to_read(order)