import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.fixture
async def product(client: AsyncClient) -> dict:
    response = await client.post("/v1/products/", json={
        "name": "Тестовый Ноутбук",
        "price": 1000.0,
        "stock": 10})
    assert response.status_code == 201
    return response.json()

@pytest.fixture
async def two_products(client: AsyncClient) -> list[dict]:
    res1 = await client.post("/v1/products/", json={"name": "Товар A", "price": 100.0, "stock": 10})
    res2 = await client.post("/v1/products/", json={"name": "Товар B", "price": 200.0, "stock": 5})
    return [res1.json(), res2.json()]


class TestCreateOrderAPI:
    async def test_create_order_success(self, client: AsyncClient, product: dict):
        response = await client.post("/v1/orders/", json={
            "items": [
                {"product_id": product["id"], "quantity": 3}]})
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["product_id"] == product["id"]
        assert data["items"][0]["quantity"] == 3
        assert data["items"][0]["price"] == 1000.0

    async def test_create_order_insufficient_stock_returns_409(self, client: AsyncClient, product: dict):
        response = await client.post("/v1/orders/", json={
            "items": [
                {"product_id": product["id"], "quantity": 100}]})
        assert response.status_code == 409
        assert "Not enough stock" in response.json()["message"]

    async def test_create_order_non_existent_product_returns_404(self, client: AsyncClient):
        response = await client.post("/v1/orders/", json={
            "items": [
                {"product_id": str(uuid4()), "quantity": 1}]})
        assert response.status_code == 404


class TestGetOrderAPI:
    async def test_get_order_by_id_success(self, client: AsyncClient, product: dict):
        created = await client.post("/v1/orders/", json={
            "items": [{"product_id": product["id"], "quantity": 2}]})
        order_id = created.json()["id"]
        response = await client.get(f"/v1/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["id"] == order_id

    async def test_get_order_not_found_returns_404(self, client: AsyncClient):
        response = await client.get(f"/v1/orders/{uuid4()}")
        assert response.status_code == 404


class TestCancelOrderAPI:
    async def test_cancel_order_success(self, client: AsyncClient, product: dict):
        created = await client.post("/v1/orders/", json={
            "items": [{"product_id": product["id"], "quantity": 2}]})
        order_id = created.json()["id"]
        response = await client.delete(f"/v1/orders/{order_id}")
        assert response.status_code == 204

    async def test_double_cancel_returns_404(self, client: AsyncClient, product: dict):
        created = await client.post("/v1/orders/", json={
            "items": [{"product_id": product["id"], "quantity": 2}]})
        order_id = created.json()["id"]
        await client.delete(f"/v1/orders/{order_id}")
        response = await client.delete(f"/v1/orders/{order_id}")
        assert response.status_code == 404
