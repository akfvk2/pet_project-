import pytest
from uuid import uuid4
from datetime import datetime
from src.schemas.bookings import BookingCreate
from src.exceptions.invalid_booking import InvalidBookingRangeException


class TestValidateEndsAt:
    def test_valid_range(self):
        starts_at = datetime(2026, 1, 1, 10, 0)
        ends_at = datetime(2026, 1, 1, 11, 0)
        booking = BookingCreate(room_id=uuid4(), user_id=uuid4(), starts_at=starts_at, ends_at=ends_at)
        assert booking.ends_at == ends_at

    def test_ends_before_starts_rejected(self):
        starts_at = datetime(2026, 1, 1, 11, 0)
        ends_at = datetime(2026, 1, 1, 10, 0)
        with pytest.raises(InvalidBookingRangeException):
            BookingCreate(room_id=uuid4(), user_id=uuid4(), starts_at=starts_at, ends_at=ends_at)

    def test_ends_equal_starts_rejected(self):
        same_time = datetime(2026, 1, 1, 10, 0)
        with pytest.raises(InvalidBookingRangeException):
            BookingCreate(room_id=uuid4(), user_id=uuid4(), starts_at=same_time, ends_at=same_time)