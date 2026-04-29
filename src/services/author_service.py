from sqlalchemy.ext.asyncio import AsyncSession
from schemas import authors
from src.models import author, book
from src.repositories.author import AuthorRepository
from uuid import UUID
from src.exceptions.not_found import NotFoundException
import logging

logger = logging.getLogger(__name__)

class AuthorService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.authors_repo = AuthorRepository(self.session)

    async def _get_author_or_fail(self, author_id: UUID):
        author_entity = await self.authors_repo.get_by_id(author_id)
        if not author_entity:
            logger.error(
                f"Entity 'Author' with id {author_id} not found",
                extra={"author_id": author_id}
            )
            raise NotFoundException("Author not found")
        return author_entity

    async def create_author(self, author_in: authors.AuthorCreate):
        author_entity = author.Author.from_schema(author_in)
        db_author = await self.authors_repo.create(author_entity)
        return authors.AuthorRead.model_validate(db_author)

    async def get_author_by_id(self, author_id: UUID):
        author_entity = await self._get_author_or_fail(author_id)
        return authors.AuthorRead.model_validate(author_entity)

    async def update_author(self, author_id: UUID, author_in: authors.AuthorUpdate):
        author_entity = await self._get_author_or_fail(author_id)
        update_data = author_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(author_entity, key, value)
        updated_author = await self.authors_repo.update(author_entity)
        return authors.AuthorRead.model_validate(updated_author)

    async def delete_author(self, author_id: UUID):
        author_entity = await self._get_author_or_fail(author_id)
        await self.authors_repo.delete(author_entity)
        return True