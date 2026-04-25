from src.repositories.BaseRepository import BaseRepository
from src.models.author import Author
from sqlalchemy.ext.asyncio import AsyncSession

class AuthorRepository(BaseRepository[Author]):
    def __init__(self, session: AsyncSession):
        super().__init__(Author, session)