from typing import Annotated
from fastapi import Depends
from src.schemas.warehouse_orders import OrderRead
from src.models.order import OrderModel


class OrderMapper:
    def to_read(self, order: OrderModel) -> OrderRead:
        return OrderRead.model_validate(order)


