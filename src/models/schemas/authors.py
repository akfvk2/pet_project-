from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from src.models.schemas.books import BookBase, BookRead
from datetime import date

class AuthorBase(BaseModel):
    name: str
    biography: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None


class AuthorCreate(AuthorBase):
    books: Optional[List[BookBase]] = None


class AuthorUpdate(AuthorBase):
    books: Optional[List[BookBase]] = None


class AuthorRead(AuthorBase):
    id: int
    books: List[BookRead] = None

    model_config = ConfigDict(from_attributes=True)
