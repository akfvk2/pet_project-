from fastapi import APIRouter, status
from src.schemas import bookings
from src.services.booking_service import BookingServiceDep
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=bookings.BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(booking_in: bookings.BookingCreate, service: BookingServiceDep):
    return await service.create(booking_in)

@router.get("/{booking_id}", response_model=bookings.BookingRead)
async def read_bookings(booking_id: UUID, service: BookingServiceDep):
    return await service.get_by_id(booking_id)

@router.put("/{booking_id}", response_model=bookings.BookingRead)
async def update_booking(booking_id: UUID, booking_in: bookings.BookingUpdate, service: BookingServiceDep):
    return await service.update_time_interval(booking_id, booking_in)

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: UUID, service: BookingServiceDep):
    return await service.cancel_booking(booking_id)


