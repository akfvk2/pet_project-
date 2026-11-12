import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.fixture
async def product(client: AsyncClient) -> dict:
    response = await client.post("/v1/products/", json={
        "name": "Тестовый Товар",
        "price": 100.0,
        "stock": 10
    })
    assert response.status_code == 201
    return response.json()


class TestCreateProductAPI:
    async def test_create_product_success(self, client: AsyncClient):
        response = await client.post("/v1/products/", json={
            "name": "Мышь Logitech",
            "price": 49.99,
            "stock": 50})
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Мышь Logitech"
        assert data["price"] == "49.99"
        assert data["stock"] == 50

    async def test_create_product_long_name_fails_validation(self, client: AsyncClient):
        response = await client.post("/v1/products/", json={
            "name": "Очень Длинное Название Товара Более 20 Символов",
            "price": 100.0,
            "stock": 10})
        assert response.status_code == 422
        assert "name must be less than 20 characters" in response.text

    async def test_create_product_invalid_price_fails_validation(self, client: AsyncClient):
        response = await client.post("/v1/products/", json={
            "name": "Товар",
            "price": -10.0,
            "stock": 10})
        assert response.status_code == 422
        assert "price must be greater than 0" in response.text

    async def test_create_product_invalid_stock_fails_validation(self, client: AsyncClient):
        response = await client.post("/v1/products/", json={
            "name": "Товар",
            "price": 100.0,
            "stock": 0})
        assert response.status_code == 422
        assert "stock must be greater than 0" in response.text


class TestGetProductAPI:
    async def test_get_product_success(self, client: AsyncClient, product: dict):
        response = await client.get(f"/v1/products/{product['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == "Тестовый Товар"

    async def test_get_product_not_found(self, client: AsyncClient):
        response = await client.get(f"/v1/products/{uuid4()}")
        assert response.status_code == 404


class TestUpdateProductAPI:
    async def test_update_product_success(self, client: AsyncClient, product: dict):
        response = await client.put(f"/v1/products/{product['id']}", json={
            "name": "Обновленный Товар",
            "price": 450.0,
            "stock": 8})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Обновленный Товар"
        assert data["price"] == "450.00"
        assert data["stock"] == 8

    async def test_update_product_not_found(self, client: AsyncClient):
        response = await client.put(f"/v1/products/{uuid4()}", json={
            "name": "Тест",
            "price": 10.0,
            "stock": 10})
        assert response.status_code == 404


class TestDeleteProductAPI:
    async def test_delete_product_success(self, client: AsyncClient, product: dict):
        response = await client.delete(f"/v1/products/{product['id']}")
        assert response.status_code == 204
        get_response = await client.get(f"/v1/products/{product['id']}")
        assert get_response.status_code == 404

    async def test_delete_product_not_found(self, client: AsyncClient):
        response = await client.delete(f"/v1/products/{uuid4()}")
        assert response.status_code == 404
