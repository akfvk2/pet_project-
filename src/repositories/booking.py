from sqlalchemy.orm import selectinload
from src.repositories.base_repository import BaseRepository
from src.models.booking import BookingModel, BookingStatus
from sqlalchemy.dialects.postgresql import insert as pg_insert
from uuid import UUID
from datetime import datetime
from sqlalchemy import update, select, text
from typing import Annotated
from fastapi import Depends
from src.db import SessionDep


class BookingRepository(BaseRepository[BookingModel]):
    def __init__(self, session: SessionDep):
        super().__init__(BookingModel, session)

    async def create(self, booking: BookingModel) -> None:
        stmt = (
            pg_insert(BookingModel)
            .values(
                id=booking.id,
                room_id=booking.room_id,
                user_id=booking.user_id,
                starts_at=booking.starts_at,
                ends_at=booking.ends_at,
                status=booking.status,
            )
            .on_conflict_do_nothing(
                index_elements=["room_id", "starts_at", "ends_at"],
                index_where=text("is_deleted = false"),)
        )
        await self.session.execute(stmt)


    async def update_schedule(self, booking: BookingModel, starts_at: datetime, ends_at: datetime) -> None:
        stmt = (
            update(BookingModel)
            .where(BookingModel.id == booking.id)
            .values(starts_at=starts_at, ends_at=ends_at)
        )
        await self.session.execute(stmt)


    async def get_by_id(self, obj_id: UUID) -> BookingModel | None:
        stmt = (
            select(BookingModel)
            .where(BookingModel.id == obj_id)
            .options(selectinload(BookingModel.room), selectinload(BookingModel.user))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def cancellation_reservation(self, obj_id: UUID) -> bool:
        stmt = (
            update(BookingModel)
            .where(BookingModel.id == obj_id)
            .values(is_deleted=True, status=BookingStatus.CANCELLED.value)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def lock_room(self, room_id: UUID) -> None:
        await self.session.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:room_id))"),
            {"room_id": str(room_id)},
        )

    async def has_overlap(self, room_id: UUID, starts_at: datetime, ends_at: datetime,
                          exclude_booking_id: UUID | None = None) -> bool:
        stmt = select(BookingModel).where(
            BookingModel.room_id == room_id,
            BookingModel.is_deleted == False,
            BookingModel.starts_at < ends_at,
            BookingModel.ends_at > starts_at,
        )
        if exclude_booking_id is not None:
            stmt = stmt.where(BookingModel.id != exclude_booking_id)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

BookingRepositoryDep = Annotated[BookingRepository, Depends(BookingRepository)]