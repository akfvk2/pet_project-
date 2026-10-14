from typing import List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.config import settings
from src.repositories.booking import BookingRepository
from src.schemas.bookings import BookingCreate, BookingRead
from src.mappers.booking_mapper import BookingMapper
from src.exceptions.booking_conflict import BookingConflictException
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
        booking = BookingMapper.to_model(booking_in)
        await self.repo.lock_room(booking.room_id)
        if await self.repo.has_overlap(booking.room_id, booking.starts_at, booking.ends_at):
            raise BookingConflictException()
        created = await self.repo.create(booking)
        if not created:
            raise BookingConflictException()
        booking = await self.repo.get_by_id(booking.id)
        return BookingMapper.to_read(booking)

    async def create_batch(self, bookings_in: List[BookingCreate]) -> List[BookingRead]:
        bookings = BookingMapper.to_models(bookings_in)
        room_ids = sorted({booking.room_id for booking in bookings_in})
        for room_id in room_ids:
            await self.repo.lock_room(room_id)
        for i, a in enumerate(bookings):
            for b in bookings[i + 1:]:
                if a.room_id == b.room_id and a.starts_at < b.ends_at and b.starts_at < a.ends_at:
                    raise BookingConflictException()
        for booking in bookings:
            if await self.repo.has_overlap(booking.room_id, booking.starts_at, booking.ends_at):
                raise BookingConflictException()
        await self.repo.create_batch(bookings)
        bookings = [await self.repo.get_by_id(b.id) for b in bookings]
        return BookingMapper.to_reads(bookings)

    async def update_schedule(self, booking_id: UUID, starts_at: datetime, ends_at: datetime) -> BookingRead:
        booking = await get_by_id_or_fail(self.repo, booking_id, "Booking")
        try:
            await self.repo.lock_room(booking.room_id)
            if await self.repo.has_overlap(booking.room_id, starts_at, ends_at, exclude_booking_id=booking.id):
                raise BookingConflictException()
            updated = await self.repo.update_schedule(booking, starts_at, ends_at)
        except IntegrityError as exc:
            if exc.orig.sqlstate == settings.unique_violation_sqlstate:
                raise BookingConflictException() from exc
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




