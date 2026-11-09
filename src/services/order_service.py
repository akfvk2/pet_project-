from uuid import UUID, uuid4
from src.dependencies import OrderRepositoryDep
from src.dependencies import OrderMapperDep
from src.schemas.warehouse_orders import OrderCreate, OrderRead
from src.models.order import OrderModel
from src.models.order_item import OrderItemModel
from src.exceptions.not_found import NotFoundException
from src.services.service_helpers import get_by_id_or_fail
from typing import Annotated
from fastapi import Depends
from src.services.order_inventory_service import OrderInventoryService


class OrderService:
    def __init__(self, order_repo: OrderRepositoryDep, inventory_service: Annotated[OrderInventoryService, Depends(OrderInventoryService)], mapper: OrderMapperDep,):
        self.order_repo = order_repo
        self.inventory_service = inventory_service
        self.mapper = mapper

    async def create_order(self, order_in: OrderCreate) -> OrderRead:
        products_by_id = await self.inventory_service.reserve_stock(order_in.items)
        items = [OrderItemModel(
                    id=uuid4(),
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=products_by_id[item.product_id].price)
        for item in order_in.items]
        order = OrderModel(id=uuid4(), items=items)
        created_order = await self.order_repo.create(order)
        return self.mapper.to_read(created_order)

    async def cancel_order(self, order_id: UUID) -> bool:
        order = await get_by_id_or_fail(self.order_repo, order_id, "Order")
        cancelled = await self.order_repo.cancel_order(order_id)
        if not cancelled:
            raise NotFoundException(f"Order {order_id} not found")
        await self.inventory_service.restore_stock(order.items)
        return True

    async def get_by_id(self, order_id: UUID) -> OrderRead:
        order = await get_by_id_or_fail(self.order_repo, order_id, "Order")
        return self.mapper.to_read(order)