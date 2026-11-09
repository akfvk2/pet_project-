from typing import Annotated
from fastapi import Depends
from src.mappers.booking_mapper import BookingMapper
from src.mappers.order_mapper import OrderMapper
from src.mappers.product_mapper import ProductMapper
from src.mappers.room_mapper import RoomMapper
from src.repositories.booking import BookingRepository
from src.repositories.order import OrderRepository
from src.repositories.product import ProductRepository
from src.repositories.room import RoomRepository


OrderMapperDep = Annotated[OrderMapper, Depends(OrderMapper)]
ProductMapperDep = Annotated[ProductMapper, Depends(ProductMapper)]
BookingMapperDep = Annotated[BookingMapper, Depends(BookingMapper)]
RoomMapperDep = Annotated[RoomMapper, Depends(RoomMapper)]
BookingRepositoryDep = Annotated[BookingRepository, Depends(BookingRepository)]
OrderRepositoryDep = Annotated[OrderRepository, Depends(OrderRepository)]
ProductRepositoryDep = Annotated[ProductRepository, Depends(ProductRepository)]
RoomRepositoryDep = Annotated[RoomRepository, Depends(RoomRepository)]
