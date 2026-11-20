from typing import Annotated
from fastapi import Depends
from src.mappers.booking_mapper import BookingMapper
from src.repositories.booking import BookingRepository

BookingMapperDep = Annotated[BookingMapper, Depends(BookingMapper)]
BookingRepositoryDep = Annotated[BookingRepository, Depends(BookingRepository)]