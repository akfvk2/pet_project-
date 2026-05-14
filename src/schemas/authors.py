from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator
from schemas.books import BookBase, BookRead
from datetime import date
from uuid import UUID
from src.exceptions.validation_error import ValidationException
from src.schemas.books import BookCreate
from src.models.author import Author
from src.models.book import Book

class AuthorBase(BaseModel):
    name: str
    biography: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValidationException(message='Name is required')
        if len(cleaned_value) < 2:
            raise ValidationException(message='Name must be at least 2 characters')
        return cleaned_value

    @field_validator( 'biography', 'nationality')
    @classmethod
    def validate_biography_nationality(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_value = value.strip()
        if len(cleaned_value) < 2:
            raise ValidationException(message='Field must contain at least 2 characters')
        return cleaned_value


class AuthorCreate(AuthorBase):
    books: list[BookCreate]

    def to_model(self):
        author_data = self.model_dump(exclude={"books"})
        author_entity = Author(**author_data)
        author_entity.books = [Book(**b.model_dump()) for b in self.books]
        return author_entity
    

class AuthorUpdate(AuthorBase):
    name: Optional[str] = None

    def update_model(self, author_entity):
        update_data = self.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(author_entity, key, value)
        return author_entity

class AuthorRead(AuthorBase):
    id: UUID
    books: List[BookRead] = None
    model_config = ConfigDict(from_attributes=True)
