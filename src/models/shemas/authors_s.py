from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str


class BookRead(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AuthorBase(BaseModel):
    name: str


class AuthorCreate(AuthorBase):
    books: Optional[List[BookBase]] = None


class AuthorUpdate(AuthorBase):
    books: Optional[List[BookBase]] = None


class AuthorRead(AuthorBase):
    id: int
    books: List[BookRead] = None

    model_config = ConfigDict(from_attributes=True)
