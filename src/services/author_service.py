from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schemas import authors
from src.models import users
from src.repositories.repositories import AuthorRepository
from uuid import uuid4
from src.exceptions.common import NotFoundException
import logging

logger = logging.getLogger(__name__)

class AuthorService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.authors_repo = AuthorRepository(self.session)

    async def create_author(self, author_in: authors.AuthorCreate):
        author_entity = users.Author(**author_in.model_dump())
        db_author = await self.authors_repo.create(author_entity)
        return authors.AuthorRead.model_validate(db_author)


    async def get_author_by_id(self, author_id: uuid4()):
        author_entity = await self.authors_repo.get_by_id(author_id)
        if not author_entity:
            logger.error(
                f"Entity 'Author' with id {author_id} not found",
                extra={"author_id": author_id}
            )
            raise NotFoundException("Author not found")
        return authors.AuthorRead.model_validate(author_entity)


    async def update_author(self, author_id: uuid4(), author_in: authors.AuthorUpdate):
        author_entity = await self.authors_repo.get_by_id(author_id)
        if not author_entity:
            logger.error(
                f"Entity 'Author' with id {author_id} not found",
                extra={"author_id": author_id}
            )
            raise NotFoundException("Author not found")
        update_data = author_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(author_entity, key, value)
        updated_author = await self.authors_repo.update(author_entity)
        return authors.AuthorRead.model_validate(updated_author)


    async def delete_author(self, author_id: uuid4()):
        author_entity = await self.authors_repo.get_by_id(author_id)
        if not author_entity:
            logger.error(
                f"Entity 'Author' with id {author_id} not found",
                extra={"author_id": author_id}
            )
            raise NotFoundException("Author not found")
        await self.authors_repo.delete(author_entity)
        return True