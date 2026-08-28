from datetime import datetime
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.services.author_service import AuthorService
from src.schemas.authors import AuthorCreate, AuthorUpdate, AuthorRead
from src.exceptions.not_found import NotFoundException
from src.models.author import Author
from src.models.book import Book
import src.services.author_service as svc_module


@pytest.fixture
def author_service(db_session, redis_client):
    service = AuthorService(session=db_session)
    svc_module.redis_client = redis_client
    return service

@pytest.fixture
def sample_author():
    author = Author(
        name="Толстой",
        biography="Русский писатель",
        birth_date=datetime(1828, 9, 9),
        nationality="Русский"
    )
    author.id = uuid4()
    author.books = [Book(title="Война и мир", page_count=100, genre="Роман")]
    author.books[0].id = uuid4()
    author.books[0].author = None
    return author

@pytest.fixture
def updated_author():
    author = Author(
        name="Достоевский",
        biography="Русский писатель",
        birth_date=datetime(1821, 11, 11),
        nationality="Русский"
    )
    author.id = uuid4()
    author.books = [Book(title="Преступление и наказание", page_count=600, genre="Роман")]
    author.books[0].id = uuid4()
    author.books[0].author = None
    return author

class TestAuthorService:
    async def test_cache_miss_fetches_from_db(self, author_service, redis_client, sample_author):
        author_service.authors_repo.get_by_id = AsyncMock(return_value=sample_author)
        result = await author_service.get_author_by_id(sample_author.id)
        assert result.name == 'Толстой'
        cached = await redis_client.get(f"author:{sample_author.id}")
        assert cached is not None

    async def test_cache_hit_skips_db(self, author_service, redis_client, sample_author):
        author_read = AuthorRead.model_validate(sample_author)
        await redis_client.setex(f"author:{sample_author.id}", 300, author_read.model_dump_json())
        author_service.authors_repo.get_by_id = AsyncMock()
        await author_service.get_author_by_id(sample_author.id)
        author_service.authors_repo.get_by_id.assert_not_called()

    async def test_not_found_raises_exception(self, author_service):
        author_service.authors_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await author_service.get_author_by_id(uuid4())

    async def test_create_returns_user_read(self, author_service, sample_author):
        author_service.authors_repo.create = AsyncMock(return_value=sample_author)
        author_in = AuthorCreate(
    name="Толстой",
    books=[{"title": "Война и мир", "page_count": 100, "genre": "Роман"}])
        result = await author_service.create_author(author_in)
        assert result.name == "Толстой"

    async def test_update_success(self, author_service, sample_author, updated_author):
        author_service.authors_repo.get_by_id = AsyncMock(return_value=sample_author)
        author_service.authors_repo.update = AsyncMock(return_value=updated_author)
        author_in = AuthorUpdate(
            name="Достоевский",
            books=[{"title": "Преступление и наказание", "page_count": 600, "genre": "Роман"}])
        result = await author_service.update_author(sample_author.id, author_in)
        assert result.name == "Достоевский"
        author_service.authors_repo.update.assert_called_once()

    async def test_update_clears_cache(self, author_service, redis_client, sample_author, updated_author):
        author_service.authors_repo.get_by_id = AsyncMock(return_value=sample_author)
        author_service.authors_repo.update = AsyncMock(return_value=updated_author)
        await author_service.update_author(
            sample_author.id,
            AuthorUpdate(
                name="Достоевский",
                books=[{"title": "Преступление и наказание", "page_count": 600, "genre": "Роман"}]))
        cached = await redis_client.get(f"author:{sample_author.id}")
        assert cached is not None

    async def test_update_not_found(self, author_service):
        author_service.authors_repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await author_service.update_author(
                uuid4(),
                AuthorUpdate(
                    name="Достоевский",
                    books=[{"title": "Преступление и наказание", "page_count": 600, "genre": "Роман"}]))

    async def test_delete_clears_cache(self, author_service, redis_client, sample_author):
        author_service.authors_repo.get_by_id = AsyncMock(return_value=sample_author)
        author_service.authors_repo.delete = AsyncMock()
        await author_service.delete_author(sample_author.id)
        cached = await redis_client.get(f"author:{sample_author.id}")
        assert cached is None