import pytest
from uuid import uuid4
from src.mappers.product_mapper import ProductMapper
from src.services.product_service import ProductService
from src.schemas.products import ProductCreate, ProductUpdate
from src.exceptions.not_found import NotFoundException
from src.repositories.product import ProductRepository
from unittest.mock import AsyncMock, Mock
from decimal import Decimal



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

    async def test_create_calls_mapper(self):
        db_product = Mock()
        repo = Mock()
        repo.create = AsyncMock(return_value=db_product)
        mapper = Mock()
        expected_result = Mock()
        mapper.to_read.return_value = expected_result
        service = ProductService(repo=repo, mapper=mapper)
        product_in = ProductCreate(
            name="стол",
            price=Decimal("120"),
            stock=20)
        result = await service.create(product_in)
        repo.create.assert_awaited_once()
        created_product = repo.create.await_args.args[0]
        assert created_product.name == "стол"
        assert created_product.price == Decimal("120")
        assert created_product.stock == 20
        mapper.to_read.assert_called_once_with(db_product)
        assert result is expected_result


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

    async def test_get_by_id_calls_mapper(self):
        product_id = uuid4()
        db_product = Mock()
        repo = Mock()
        repo.get_by_id = AsyncMock(return_value=db_product)
        mapper = Mock()
        expected_result = Mock()
        mapper.to_read.return_value = expected_result
        service = ProductService(repo=repo, mapper=mapper)
        result = await service.get_by_id(product_id)
        repo.get_by_id.assert_awaited_once_with(product_id)
        mapper.to_read.assert_called_once_with(db_product)
        assert result is expected_result


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

    async def test_update_calls_mapper(self):
        product_id = uuid4()
        db_product = Mock()
        updated_product = Mock()
        repo = Mock()
        repo.get_by_id = AsyncMock(return_value=db_product)
        repo.update = AsyncMock(return_value=updated_product)
        mapper = Mock()
        expected_result = Mock()
        mapper.to_read.return_value = expected_result
        service = ProductService(repo=repo, mapper=mapper)
        product_in = ProductUpdate(price=Decimal("140"), stock=10)
        result = await service.update(product_id, product_in)
        repo.get_by_id.assert_awaited_once_with(product_id)
        repo.update.assert_awaited_once_with(db_product)
        mapper.to_read.assert_called_once_with(updated_product)
        assert result is expected_result


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