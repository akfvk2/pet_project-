import pytest
from uuid import uuid4


class TestCreateUser:
    async def test_success(self, client):
        response = await client.post("/v1/users/", json={
    "username": "testuser",
    "email": "testuser@gmail.com",
    "age": 25,
    "order_title": "Test Order",
    "order_price": 10.0
})
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data

    async def test_invalid_email_domain(self, client):
        response = await client.post("/v1/users/", json={
    "username": "testuser",
    "email": "testuser@fffgmail.com",
    "age": 25,
    "order_title": "Test Order",
    "order_price": 10.0
})
        assert response.status_code == 422

    async def test_short_username(self, client):
        response = await client.post("/v1/users/", json={
    "username": "t",
    "email": "testuser@gmail.com",
    "age": 25,
    "order_title": "Test Order",
    "order_price": 10.0
})
        assert response.status_code == 422


class TestGetUser:
    async def test_success(self, client):
        create = await client.post("/v1/users/", json={
    "username": "testuser",
    "email": "testuser@gmail.com",
    "age": 25,
    "order_title": "Test Order",
    "order_price": 10.0
})
        user_id = create.json()["id"]

        response = await client.get(f"/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    async def test_not_found(self, client):
        response = await client.get(f"/v1/users/{uuid4()}")
        assert response.status_code == 404


class TestUpdateUser:
    async def test_success(self, client):
        create = await client.post("/v1/users/", json={
    "username": "testuser",
    "email": "testuser@gmail.com",
    "age": 25,
    "order_title": "Test Order",
    "order_price": 10.0
})
        user_id = create.json()["id"]

        response = await client.put(f"/v1/users/{user_id}", json={
    "username": "updated",
    "email": "update@gmail.com",
    "age": 30,
    "order_title": "update",
    "order_price": 11.0
})
        assert response.status_code == 200
        assert response.json()["username"] == "updated"


class TestDeleteUser:
    async def test_success(self, client):
        create = await client.post("/v1/users/", json={
    "username": "testuser",
    "email": "testuser@gmail.com",
    "age": 25,
    "order_title": "Test Order",
    "order_price": 10.0
}
)
        user_id = create.json()["id"]

        response = await client.delete(f"/v1/users/{user_id}")
        assert response.status_code == 204

