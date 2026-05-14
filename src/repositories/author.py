from src.repositories.base_repository import BaseRepository
from src.models.author import Author
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID


class AuthorRepository(BaseRepository[Author]):
    def __init__(self, session: AsyncSession):
        super().__init__(Author, session)

    async def get_by_id(self, obj_id: UUID) -> Author | None:
        stmt = (
            select(Author)
            .where(Author.id == obj_id)
            .options(selectinload(Author.books))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()