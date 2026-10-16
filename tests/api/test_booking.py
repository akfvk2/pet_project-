import pytest
from uuid import uuid4
from src.repositories.room import RoomRepository
from src.repositories.user import UserRepository
from src.models.room import RoomModel
from src.models.user import UserModel


@pytest.fixture
async def room(db_session):
    repo = RoomRepository(db_session)
    return await repo.create(RoomModel(id=uuid4(), roomname="API Room"))



@pytest.fixture
async def user(db_session):
    repo = UserRepository(db_session)
    return await repo.create(UserModel(id=uuid4(), username="api_tester", email="api@example.com", age=30))



class TestCreateBooking:
    async def test_success(self, client, room, user):
        response = await client.post("/v1/bookings/", json={
            "room_id": str(room.id),
            "user_id": str(user.id),
            "starts_at": "2026-02-01T10:00:00",
            "ends_at": "2026-02-01T11:00:00",
        })
        assert response.status_code == 201
        assert response.json()["room"]["id"] == str(room.id)

    async def test_overlap_returns_409(self, client, room, user):
        await client.post("/v1/bookings/", json={
            "room_id": str(room.id),
            "user_id": str(user.id),
            "starts_at": "2026-02-02T10:00:00",
            "ends_at": "2026-02-02T11:00:00",
        })
        response = await client.post("/v1/bookings/", json={
            "room_id": str(room.id),
            "user_id": str(user.id),
            "starts_at": "2026-02-02T10:30:00",
            "ends_at": "2026-02-02T11:30:00",
        })
        assert response.status_code == 409

    async def test_invalid_range_returns_400(self, client, room, user):
        response = await client.post("/v1/bookings/", json={
            "room_id": str(room.id),
            "user_id": str(user.id),
            "starts_at": "2026-02-03T11:00:00",
            "ends_at": "2026-02-03T10:00:00",
        })
        assert response.status_code == 400
