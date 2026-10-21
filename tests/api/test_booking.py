import pytest
from httpx import AsyncClient


@pytest.fixture
async def room(client: AsyncClient) -> dict:
    response = await client.post("/v1/rooms/", json={"roomname": "API Room"})
    return response.json()



@pytest.fixture
async def user(client: AsyncClient) -> dict:
    response = await client.post("/v1/users/", json={
        "username": "api_tester",
        "email": "api_tester@gmail.com",
        "age": 30,
        "order_title": "Test Order",
        "order_price": 10.0,
    })
    return response.json()



class TestCreateBooking:
    async def test_success(self, client: AsyncClient, room: dict, user: dict):
        response = await client.post("/v1/bookings/", json={
            "room_id": room["id"],
            "user_id": user["id"],
            "starts_at": "2026-02-01T10:00:00",
            "ends_at": "2026-02-01T11:00:00",
        })
        assert response.status_code == 201
        assert response.json()["room"]["id"] == room["id"]

    async def test_overlap_returns_409(self, client: AsyncClient, room: dict, user: dict):
        await client.post("/v1/bookings/", json={
            "room_id": room["id"],
            "user_id": user["id"],
            "starts_at": "2026-02-02T10:00:00",
            "ends_at": "2026-02-02T11:00:00",
        })
        response = await client.post("/v1/bookings/", json={
            "room_id": room["id"],
            "user_id": user["id"],
            "starts_at": "2026-02-02T10:30:00",
            "ends_at": "2026-02-02T11:30:00",
        })
        assert response.status_code == 409

    async def test_invalid_range_returns_400(self, client: AsyncClient, room: dict, user: dict):
        response = await client.post("/v1/bookings/", json={
            "room_id": room["id"],
            "user_id": user["id"],
            "starts_at": "2026-02-03T11:00:00",
            "ends_at": "2026-02-03T10:00:00",
        })
        assert response.status_code == 400
