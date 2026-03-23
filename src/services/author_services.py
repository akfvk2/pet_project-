from sqlalchemy.ext.asyncio import AsyncSession
from src.models.shemas import authors_s
from src.models import users
from src.repositories.repositories import AuthorRepository
from src.exceptions import NotFoundException


class AuthorService:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_author(self, author_in: authors_s.AuthorCreate):
        author_entity = users.Author(**author_in.model_dump())
        author_repo = AuthorRepository(self.session)
        db_author = await author_repo.create(author_entity)
        return authors_s.AuthorRead.model_validate(db_author)


    async def get_author_by_id(self, author_id: int):
        author_repo = AuthorRepository(self.session)
        author_entity = await author_repo.get_by_id(author_id)
        if not author_entity:
            raise NotFoundException("Author not found")
        return authors_s.AuthorRead.model_validate(author_entity)


    async def update_author(self, author_id: int, author_in: authors_s.AuthorUpdate):
        author_repo = AuthorRepository(self.session)
        author_entity = await author_repo.get_by_id(author_id)
        if not author_entity:
            raise NotFoundException("Author not found")
        update_data = author_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(author_entity, key, value)
        updated_author = await author_repo.update(author_entity)
        return authors_s.AuthorRead.model_validate(updated_author)


    async def delete_author(self, author_id: int):
        author_repo = AuthorRepository(self.session)
        author_entity = await author_repo.get_by_id(author_id)
        if not author_entity:
            raise NotFoundException("Author not found")
        await author_repo.delete(author_entity)
        return True