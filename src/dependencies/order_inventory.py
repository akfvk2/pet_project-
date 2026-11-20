from typing import Annotated
from fastapi import Depends
from src.services.order_inventory_service import OrderInventoryService


OrderInventoryServiceDep = Annotated[OrderInventoryService, Depends(OrderInventoryService)]