from typing import Annotated
from fastapi import Depends
from src.schemas.warehouse_orders import OrderRead
from src.models.order import OrderModel
from  uuid import uuid4
from src.models.order_item import OrderItemModel


class OrderMapper:
    def to_read(self, order: OrderModel) -> OrderRead:
        return OrderRead.model_validate(order)

    def to_model(self, items: list[OrderItemModel]) -> OrderModel:
        return OrderModel(id=uuid4(), items=items)