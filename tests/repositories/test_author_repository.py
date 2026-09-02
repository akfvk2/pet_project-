from src.repositories.author import AuthorRepository
from src.models.author import Author
import pytest_asyncio
from uuid import uuid4
from datetime import datetime


@pytest_asyncio.fixture
async def repo(db_session):
    return AuthorRepository(db_session)

class TestAuthorRepository:
    async def test_create_author(self, repo):
        author = Author(name="test",
                        biography="test",
                        birth_date=datetime(1828, 9, 9),
                        nationality="test")
        created_author = await repo.create(author)
        assert created_author.id is not None
        assert created_author.name == "test"

    async def test_get_by_id(self, repo):
        author = Author(name="test",
                        biography="test",
                        birth_date=datetime(1828, 9, 9),
                        nationality="test")
        created_author = await repo.create(author)
        found = await repo.get_by_id(created_author.id)
        assert found is not None
        assert found.name == "test"

    async def test_get_by_id_not_found(self, repo):
        found = await repo.get_by_id(uuid4())
        assert found is None

    async def test_update_author(self, repo):
        author = Author(name="test",
                        biography="test",
                        birth_date=datetime(1828, 9, 9),
                        nationality="test")
        created_author = await repo.create(author)
        created_author.name = "updated"
        created_author.biography = "updated"
        updated = await repo.update(created_author)
        assert updated.name == "updated"
        assert updated.biography == "updated"

    async def test_soft_delete(self, repo):
        author = Author(name="test",
                        biography="test",
                        birth_date=datetime(1828, 9, 9),
                        nationality="test")
        created_author = await repo.create(author)
        await repo.delete(created_author)
        assert created_author.is_deleted is True
