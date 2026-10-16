from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.booking import BookingRepository
from src.schemas.bookings import BookingCreate, BookingRead, BookingUpdate
from src.mappers.booking_mapper import BookingMapper
from src.exceptions.already_exists import AlreadyExistsException
from src.exceptions.not_found import NotFoundException
from src.services.service_helpers import get_by_id_or_fail
from fastapi import Depends
from src.db import get_session

async def get_booking_repository(session: AsyncSession = Depends(get_session)) -> BookingRepository:
    return BookingRepository(session)

class BookingService:
    def __init__(self, repo: BookingRepository = Depends(get_booking_repository)):
        self.repo = repo

    async def create(self, booking_in: BookingCreate) -> BookingRead:
        booking = booking_in.to_model()
        await self.repo.lock_room(booking.room_id)
        if await self.repo.has_overlap(booking.room_id, booking.starts_at, booking.ends_at):
            raise AlreadyExistsException()
        await self.repo.create(booking)
        booking = await self.repo.get_by_id(booking.id)
        return BookingMapper.to_read(booking)

    async def update_time_interval(self, booking_id: UUID, booking_in: BookingUpdate) -> BookingRead:
        booking = await get_by_id_or_fail(self.repo, booking_id, "Booking")
        await self.repo.lock_room(booking.room_id)
        if await self.repo.has_overlap(booking.room_id, booking_in.starts_at, booking_in.ends_at, exclude_booking_id=booking.id):
            raise AlreadyExistsException()
        updated = await self.repo.update_schedule(booking, booking_in.starts_at, booking_in.ends_at)
        if not updated:
            raise NotFoundException("Booking not found")
        booking_in.update_model(booking)
        return BookingMapper.to_read(booking)

    async def cancel_booking(self, booking_id: UUID) -> bool:
        cancelled = await self.repo.cancellation_reservation(booking_id)
        if not cancelled:
            raise NotFoundException("Booking not found")
        return True


    async def get_by_id(self, booking_id: UUID) -> BookingRead:
        booking = await get_by_id_or_fail(self.repo, booking_id, "Booking")
        return BookingMapper.to_read(booking)




