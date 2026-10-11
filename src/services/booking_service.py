from typing import List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.config import settings
from src.repositories.booking import BookingRepository
from src.schemas.bookings import BookingCreate, BookingRead
from src.mappers.booking_mapper import BookingMapper
from src.exceptions.booking_conflict import BookingConflictError
from src.exceptions.not_found import NotFoundException
from src.services.service_helpers import get_by_id_or_fail



class BookingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BookingRepository(self.session)

    async def create(self, booking_in: BookingCreate) -> BookingRead:
        booking = booking_in.to_model()
        created = await self.repo.create(booking)
        if not created:
            raise BookingConflictError()
        booking = await self.repo.get_by_id(booking.id)
        return BookingMapper.to_read(booking)

    async def create_batch(self, bookings_in: List[BookingCreate]) -> List[BookingRead]:
        bookings = [booking_in.to_model() for booking_in in bookings_in]
        inserted_count = await self.repo.create_batch(bookings)
        if  inserted_count != len(bookings_in):
            raise BookingConflictError()
        bookings = [await self.repo.get_by_id(b.id) for b in bookings]
        return BookingMapper.to_reads(bookings)

    async def update_schedule(self, booking_id: UUID, starts_at: datetime, ends_at: datetime) -> BookingRead:
        booking = await get_by_id_or_fail(self.repo, booking_id, "Booking")
        try:
            updated = await self.repo.update_schedule(booking, starts_at, ends_at)
        except IntegrityError as exc:
            if exc.orig.sqlstate == settings.exclusion_violation_sqlstate:
                raise BookingConflictError() from exc
            raise
        if not updated:
            raise NotFoundException("Booking not found")
        booking.starts_at = starts_at
        booking.ends_at = ends_at
        return BookingMapper.to_read(booking)

    async def cancel_booking(self, booking_id: UUID) -> bool:
        cancelled = await self.repo.cancellation_reservation(booking_id)
        if not cancelled:
            raise NotFoundException("Booking not found")
        return True


    async def get_by_id(self, booking_id: UUID) -> BookingRead:
        booking = await get_by_id_or_fail(self.repo, booking_id, "Booking")
        return BookingMapper.to_read(booking)




