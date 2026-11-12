import pytest
from uuid import uuid4
from src.mappers.product_mapper import ProductMapper
from src.services.product_service import ProductService
from src.schemas.products import ProductCreate, ProductUpdate
from src.exceptions.not_found import NotFoundException
from src.repositories.product import ProductRepository


@pytest.fixture
def product_repo(db_session):
    return ProductRepository(db_session)

@pytest.fixture
def service(db_session):
    return ProductService(ProductRepository(db_session), ProductMapper())


class TestCreate:
    async def test_create_success(self, service):
        result = await service.create(ProductCreate(
            name="стол",
            price="120",
            stock="20"
        ))
        assert result.name == "стол"
        assert result.id is not None


class TestGet:
    async def test_get_by_id_success(self, service):
        created = await service.create(ProductCreate(name="стол",
            price="120",
            stock="20"))
        result = await service.get_by_id(created.id)
        assert result.id == created.id
        assert result.name == "стол"

    async def test_get_by_id_not_found(self, service):
        with pytest.raises(NotFoundException):
            await service.get_by_id(uuid4())


class TestUpdate:
    async def test_update_success(self, service):
        created = await service.create(ProductCreate(name="стол",
            price="120",
            stock="20"))
        updated = await service.update(created.id, ProductUpdate(price="140", stock="10"))
        assert updated.price == 140.0
        assert updated.id is not None

    async def test_update_not_found(self, service):
        with pytest.raises(NotFoundException):
            await service.update(uuid4(), ProductUpdate(name="x", price=1, stock=1))


class TestDelete:
    async def test_delete_success(self, service, product_repo):
        created = await service.create(ProductCreate(name="стол",
            price="120",
            stock="20"))
        result = await service.delete(created.id)
        assert result is True
        product = await product_repo.get_by_id(created.id)
        assert await product_repo.get_by_id(created.id) is None

    async def test_delete_not_found(self, service):
        with pytest.raises(NotFoundException):
            await service.delete(uuid4())