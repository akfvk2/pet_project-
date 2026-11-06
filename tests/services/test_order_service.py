import pytest
import pytest_asyncio
from uuid import uuid4
from src.mappers.warehouse_order_mapper import OrderMapper
from src.services.order_service import OrderService
from src.schemas.warehouse_orders import OrderCreate
from src.schemas.order_items import OrderItemCreate
from src.exceptions.insufficient import InsufficientException
from src.exceptions.not_found import NotFoundException
from src.repositories.order import OrderRepository
from src.repositories.product import ProductRepository
from src.models.product import ProductModel


@pytest_asyncio.fixture
async def product(db_session):
    repo = ProductRepository(db_session)
    created = await repo.create(ProductModel(id=uuid4(), name="Widget", price=100.0, stock=10))
    await db_session.commit()
    return created


@pytest.fixture
def product_repo(db_session):
    return ProductRepository(db_session)


@pytest.fixture
def service(db_session):
    return OrderService(OrderRepository(db_session), ProductRepository(db_session), OrderMapper())


def make_order_create(product_id, quantity):
    return OrderCreate(items=[OrderItemCreate(product_id=product_id, quantity=quantity)])


class TestCreate:
    async def test_create_success(self, service, product, db_session):
        result = await service.create_order(make_order_create(product.id, 3))
        assert result.status == "pending"
        assert result.items[0].product_id == product.id
        assert result.items[0].quantity == 3
        await db_session.refresh(product)
        assert product.stock == 7

    async def test_insufficient_stock_rejected(self, service, product, db_session):
        with pytest.raises(InsufficientException):
            await service.create_order(make_order_create(product.id, 100))
        await db_session.refresh(product)
        assert product.stock == 10


class TestCancel:
    async def test_cancel_restores_stock(self, service, product, db_session):
        created = await service.create_order(make_order_create(product.id, 4))
        await db_session.refresh(product)
        assert product.stock == 6
        await service.cancel_order(created.id)
        await db_session.refresh(product)
        assert product.stock == 10

    async def test_double_cancel_does_not_double_restore(self, service, product, db_session):
        created = await service.create_order(make_order_create(product.id, 4))
        await service.cancel_order(created.id)
        with pytest.raises(NotFoundException):
            await service.cancel_order(created.id)
        await db_session.refresh(product)
        assert product.stock == 10

    async def test_cancel_not_found(self, service):
        with pytest.raises(NotFoundException):
            await service.cancel_order(uuid4())


class TestPriceSnapshot:
    async def test_price_change_does_not_affect_existing_order(self, service, product, product_repo, db_session):
        created = await service.create_order(make_order_create(product.id, 2))
        assert created.items[0].price == 100.0
        product.price = 500.0
        await product_repo.update(product)
        fetched = await service.get_by_id(created.id)
        assert fetched.items[0].price == 100.0


class TestMultipleItems:
    async def test_create_order_multiple_products_success(self, service, product_repo, db_session):
        p1 = await product_repo.create(ProductModel(id=uuid4(), name="P1", price=10.0, stock=10))
        p2 = await product_repo.create(ProductModel(id=uuid4(), name="P2", price=20.0, stock=5))
        await db_session.commit()
        order_in = OrderCreate(items=[
            OrderItemCreate(product_id=p1.id, quantity=3),
            OrderItemCreate(product_id=p2.id, quantity=2)])
        result = await service.create_order(order_in)
        await db_session.refresh(p1)
        await db_session.refresh(p2)
        assert p1.stock == 7
        assert p2.stock == 3
        assert len(result.items) == 2

    async def test_atomic_rollback_if_one_product_insufficient(self, service, product_repo, db_session):
        p1 = await product_repo.create(ProductModel(id=uuid4(), name="P1", price=10.0, stock=10))
        p2 = await product_repo.create(ProductModel(id=uuid4(), name="P2", price=20.0, stock=2))
        await db_session.commit()
        order_in = OrderCreate(items=[
            OrderItemCreate(product_id=p1.id, quantity=1),
            OrderItemCreate(product_id=p2.id, quantity=5)])
        with pytest.raises(InsufficientException):
            await service.create_order(order_in)
        await db_session.refresh(p1)
        await db_session.refresh(p2)
        assert p1.stock == 10
        assert p2.stock == 2


class TestBoundaryConditions:
    async def test_exact_stock_purchase_allowed(self, service, product, db_session):
        result = await service.create_order(make_order_create(product.id, 10))
        await db_session.refresh(product)
        assert product.stock == 0
        assert result.status == "pending"
