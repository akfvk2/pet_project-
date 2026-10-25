from uuid import UUID
from src.repositories.booking import BookingRepositoryDep
from src.schemas.bookings import BookingCreate, BookingRead, BookingUpdate
from src.mappers.booking_mapper import BookingMapperDep
from src.exceptions.already_exists import AlreadyExistsException
from src.exceptions.not_found import NotFoundException
from src.services.service_helpers import get_by_id_or_fail
from fastapi import Depends
from typing import Annotated



class BookingService:
    def __init__(self, repo: BookingRepositoryDep, mapper: BookingMapperDep):
        self.repo = repo
        self.mapper = mapper

    async def create(self, booking_in: BookingCreate) -> BookingRead:
        booking = booking_in.to_model()
        await self.repo.lock_room(booking.room_id)
        if await self.repo.has_overlap(booking.room_id, booking.starts_at, booking.ends_at):
            raise AlreadyExistsException("Room is already booked for this time range")
        await self.repo.create(booking)
        booking = await self.repo.get_by_id(booking.id)
        return self.mapper.to_read(booking)

    async def update_time_interval(self, booking_id: UUID, booking_in: BookingUpdate) -> BookingRead:
        booking = await get_by_id_or_fail(self.repo, booking_id, "Booking")
        await self.repo.lock_room(booking.room_id)
        if await self.repo.has_overlap(booking.room_id, booking_in.starts_at, booking_in.ends_at, exclude_booking_id=booking.id):
            raise AlreadyExistsException("Room is already booked for this time range")
        await self.repo.update_schedule(booking, booking_in.starts_at, booking_in.ends_at)
        booking = self.mapper.update_model(booking_in, booking)
        return self.mapper.to_read(booking)

    async def cancel_booking(self, booking_id: UUID) -> bool:
        cancelled = await self.repo.cancellation_reservation(booking_id)
        if not cancelled:
            raise NotFoundException("Booking not found")
        return True


    async def get_by_id(self, booking_id: UUID) -> BookingRead:
        booking = await get_by_id_or_fail(self.repo, booking_id, "Booking")
        return self.mapper.to_read(booking)


BookingServiceDep = Annotated[BookingService, Depends(BookingService)]




