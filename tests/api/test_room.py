import pytest
from uuid import uuid4


class TestCreateRoom:
    async def test_success(self, client):
        response = await client.post("/v1/rooms/", json={"roomname": "Переговорка 1"})
        assert response.status_code == 201
        assert response.json()["roomname"] == "Переговорка 1"


class TestGetRoom:
    async def test_success(self, client):
        created = await client.post("/v1/rooms/", json={"roomname": "Переговорка 2"})
        room_id = created.json()["id"]
        response = await client.get(f"/v1/rooms/{room_id}")
        assert response.status_code == 200
        assert response.json()["roomname"] == "Переговорка 2"

    async def test_not_found(self, client):
        response = await client.get(f"/v1/rooms/{uuid4()}")
        assert response.status_code == 404


class TestDeleteRoom:
    async def test_success(self, client):
        created = await client.post("/v1/rooms/", json={"roomname": "Переговорка 3"})
        room_id = created.json()["id"]
        response = await client.delete(f"/v1/rooms/{room_id}")
        assert response.status_code == 204

    async def test_not_found(self, client):
        response = await client.delete(f"/v1/rooms/{uuid4()}")
        assert response.status_code == 404
