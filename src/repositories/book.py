from src.repositories.base_repository import BaseRepository
from src.models.book import Book
from sqlalchemy.ext.asyncio import AsyncSession

class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession):
        super().__init__(Book, session)