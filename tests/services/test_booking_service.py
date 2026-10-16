import pytest
import pytest_asyncio
import asyncio
from uuid import uuid4
from datetime import datetime
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.services.booking_service import BookingService
from src.schemas.bookings import BookingCreate, BookingUpdate
from src.exceptions.already_exists import AlreadyExistsException
from src.exceptions.not_found import NotFoundException
from src.repositories.room import RoomRepository
from src.repositories.user import UserRepository
from src.repositories.booking import BookingRepository
from src.models.room import RoomModel
from src.models.user import UserModel



@pytest_asyncio.fixture
async def room(db_session):
    repo = RoomRepository(db_session)
    created = await repo.create(RoomModel(id=uuid4(), roomname="Conference A"))
    await db_session.commit()
    return created


@pytest_asyncio.fixture
async def user(db_session):
    repo = UserRepository(db_session)
    created = await repo.create(UserModel(id=uuid4(), username="tester", email="tester@example.com", age=25))
    await db_session.commit()
    return created


@pytest.fixture
def service(db_session):
    return BookingService(BookingRepository(db_session))

@pytest.fixture
def room_repo(db_session):
    return RoomRepository(db_session)


def make_booking_create(room_id, user_id, starts_at, ends_at):
    return BookingCreate(room_id=room_id, user_id=user_id, starts_at=starts_at, ends_at=ends_at)


class TestCreate:
    async def test_create_success(self, service, room, user):
        booking_in = make_booking_create(room.id, user.id, datetime(2026, 1, 1, 10, 0), datetime(2026, 1, 1, 11, 0))
        result = await service.create(booking_in)
        assert result.room.id == room.id
        assert result.user.id == user.id

    async def test_overlapping_rejected(self, service, room, user):
        await service.create(make_booking_create(room.id, user.id, datetime(2026, 1, 2, 10, 0), datetime(2026, 1, 2, 11, 0)))
        with pytest.raises(AlreadyExistsException):
            await service.create(make_booking_create(room.id, user.id, datetime(2026, 1, 2, 10, 30), datetime(2026, 1, 2, 11, 30)))

    async def test_adjacent_bookings_allowed(self, service, room, user):
        await service.create(make_booking_create(room.id, user.id, datetime(2026, 1, 3, 10, 0), datetime(2026, 1, 3, 11, 0)))
        result = await service.create(make_booking_create(room.id, user.id, datetime(2026, 1, 3, 11, 0), datetime(2026, 1, 3, 12, 0)))
        assert result is not None

    async def test_different_rooms_no_conflict(self, service, room, user, db_session, room_repo):
        other_room = await room_repo.create(RoomModel(id=uuid4(), roomname="Conference B"))
        await db_session.commit()
        starts_at, ends_at = datetime(2026, 1, 4, 10, 0), datetime(2026, 1, 4, 11, 0)
        await service.create(make_booking_create(room.id, user.id, starts_at, ends_at))
        result = await service.create(make_booking_create(other_room.id, user.id, starts_at, ends_at))
        assert result is not None


class TestCancel:
    async def test_cancelled_booking_does_not_block_new_one(self, service, room, user):
        starts_at, ends_at = datetime(2026, 1, 5, 10, 0), datetime(2026, 1, 5, 11, 0)
        created = await service.create(make_booking_create(room.id, user.id, starts_at, ends_at))
        await service.cancel_booking(created.id)
        result = await service.create(make_booking_create(room.id, user.id, starts_at, ends_at))
        assert result is not None

    async def test_cancel_not_found(self, service):
        with pytest.raises(NotFoundException):
            await service.cancel_booking(uuid4())


class TestUpdateSchedule:
    async def test_rechecks_overlap(self, service, room, user):
        await service.create(make_booking_create(room.id, user.id, datetime(2026, 1, 6, 10, 0), datetime(2026, 1, 6, 11, 0)))
        second = await service.create(make_booking_create(room.id, user.id, datetime(2026, 1, 6, 12, 0), datetime(2026, 1, 6, 13, 0)))
        with pytest.raises(AlreadyExistsException):
            await service.update_time_interval(second.id, BookingUpdate(starts_at=datetime(2026, 1, 6, 10, 30), ends_at=datetime(2026, 1, 6, 11, 30)))

    async def test_update_success(self, service, room, user):
        booking = await service.create(make_booking_create(room.id, user.id, datetime(2026, 1, 7, 10, 0), datetime(2026, 1, 7, 11, 0)))
        updated = await service.update_time_interval(booking.id, BookingUpdate(starts_at=datetime(2026, 1, 7, 14, 0), ends_at=datetime(2026, 1, 7, 15, 0)))
        assert updated.starts_at == datetime(2026, 1, 7, 14, 0)


class TestConcurrentCreate:
    async def test_exactly_one_succeeds(self, db_url, room, user):
        engine1 = create_async_engine(db_url, poolclass=NullPool)
        engine2 = create_async_engine(db_url, poolclass=NullPool)
        session1 = async_sessionmaker(engine1, class_=AsyncSession, expire_on_commit=False)()
        session2 = async_sessionmaker(engine2, class_=AsyncSession, expire_on_commit=False)()
        service1 = BookingService(BookingRepository(session1))
        service2 = BookingService(BookingRepository(session2))

        async def create_and_commit(service, session, booking_in):
            try:
                result = await service.create(booking_in)
                await session.commit()
                return result
            except Exception as exc:
                await session.rollback()
                return exc

        starts_at, ends_at = datetime(2026, 1, 10, 10, 0), datetime(2026, 1, 10, 11, 0)
        results = await asyncio.gather(
            create_and_commit(service1, session1, make_booking_create(room.id, user.id, starts_at, ends_at)),
            create_and_commit(service2, session2, make_booking_create(room.id, user.id, starts_at, ends_at)),
        )

        successes = [r for r in results if not isinstance(r, Exception)]
        conflicts = [r for r in results if isinstance(r, AlreadyExistsException)]
        assert len(successes) == 1
        assert len(conflicts) == 1

        await session1.close()
        await session2.close()
        await engine1.dispose()
        await engine2.dispose()