from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_session
from src.schemas import bookings
from src.services.booking_service import BookingService
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=bookings.BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(booking_in: bookings.BookingCreate, service: BookingService = Depends(BookingService)):
    return await service.create(booking_in)

@router.post("/batch", response_model=list[bookings.BookingRead], status_code=status.HTTP_201_CREATED)
async def create_batch(bookings_in: list[bookings.BookingCreate], service: BookingService = Depends(BookingService)):
    return await service.create_batch(bookings_in)

@router.get("/{booking_id}", response_model=bookings.BookingRead)
async def read_bookings(booking_id: UUID, service: BookingService = Depends(BookingService)):
    return await service.get_by_id(booking_id)

@router.put("/{booking_id}", response_model=bookings.BookingRead)
async def update_booking(booking_id: UUID, booking_in: bookings.BookingUpdate, service: BookingService = Depends(BookingService)):
    return await service.update_schedule(booking_id, booking_in.starts_at, booking_in.ends_at)

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: UUID, service: BookingService = Depends(BookingService)):
    return await service.cancel_booking(booking_id)


