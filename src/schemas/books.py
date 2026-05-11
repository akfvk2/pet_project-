from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID
from src.exceptions.validation_error import ValidationException


class BookBase(BaseModel):
    title: str
    page_count: Optional[int] = None
    genre: Optional[str] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValidationException(message='Title cannot be empty')
        if len(cleaned_value) < 2:
            raise ValidationException(message='Please provide a real title')
        return cleaned_value

    @field_validator( 'genre')
    @classmethod
    def validate_genre(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_value = value.strip()
        if len(cleaned_value) < 2:
            raise ValidationException(message='The genre length must be at least 2 characters')
        return cleaned_value

    @field_validator('page_count')
    @classmethod
    def validate_page_count(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value <= 0:
            raise ValidationException(message='Page count must be greater than zero')
        if value > 1000:
            raise ValidationException(message='Page count is too large')
        return value

class BookRead(BookBase):
    id: UUID
    author_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

class BookCreate(BookBase):
    pass