from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator
from schemas.books import BookBase, BookRead
from datetime import date
from uuid import UUID

class AuthorBase(BaseModel):
    name: str
    biography: Optional[str] = None
    birth_date: Optional[date] = None
    nationality: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_string_field(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('name is required')
        if len(cleaned_value) < 2:
            raise ValueError('name is required')
        return cleaned_value

    @field_validator( 'biography', 'nationality')
    @classmethod
    def validate_string_field_op(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_value = value.strip()
        if len(cleaned_value) < 2:
            raise ValueError('Field must contain at least 2 characters')
        return cleaned_value


class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(AuthorBase):
    pass

class AuthorRead(AuthorBase):
    id: UUID
    books: List[BookRead] = None
    model_config = ConfigDict(from_attributes=True)
