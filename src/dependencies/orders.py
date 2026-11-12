from typing import Annotated
from fastapi import Depends
from src.mappers.warehouse_order_mapper import OrderMapper
from src.repositories.order import OrderRepository


OrderMapperDep = Annotated[OrderMapper, Depends(OrderMapper)]
OrderRepositoryDep = Annotated[OrderRepository, Depends(OrderRepository)]