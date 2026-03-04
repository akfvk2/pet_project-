from sqlalchemy.ext.asyncio import AsyncSession

from models import schemas
from repositories.repositories import AuthorRepository


class AuthorService:
    @staticmethod
    async def create_author(session: AsyncSession, author_in: schemas.AuthorCreate):
        return await AuthorRepository.create(session, author_in)

    @staticmethod
    async def get_author_by_id(session: AsyncSession, author_id: int):
        return await AuthorRepository.get_by_id(session, author_id)

    @staticmethod
    async def update_author(session: AsyncSession, author_id: int, author_in: schemas.AuthorUpdate):
        return await AuthorRepository.update(session, author_id, author_in)

    @staticmethod
    async def delete_author(session: AsyncSession, author_id: int):
        return await AuthorRepository.delete(session, author_id)