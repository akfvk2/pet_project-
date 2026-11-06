from fastapi import APIRouter, status
from src.schemas import warehouse_orders
from src.services.order_service import OrderService
from uuid import UUID
from fastapi import Depends
from typing import Annotated


router = APIRouter()

OrderServiceDep = Annotated[OrderService, Depends(OrderService)]

@router.post("/", response_model=warehouse_orders.OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: warehouse_orders.OrderCreate, service: OrderServiceDep):
    return await service.create_order(order_in)

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: UUID, service: OrderServiceDep):
    return await service.cancel_order(order_id)

@router.get("/{order_id}", response_model=warehouse_orders.OrderRead)
async def read_order(order_id: UUID, service: OrderServiceDep):
    return await service.get_by_id(order_id)