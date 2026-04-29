from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID

class BookBase(BaseModel):
    title: str
    page_count: Optional[int] = None
    genre: Optional[str] = None

    @field_validator('title')
    @classmethod
    def validate_string_field(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('Title cannot be empty')
        if len(cleaned_value) < 2:
            raise ValueError('Please provide a real title')
        return cleaned_value

    @field_validator( 'genre')
    @classmethod
    def validate_string_field_op(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_value = value.strip()
        if len(cleaned_value) < 2:
            raise ValueError('The genre length must be at least 2 characters')
        return cleaned_value

    @field_validator('page_count')
    @classmethod
    def validate_int(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value <= 0:
            raise ValueError('Page count must be greater than zero')
        if value > 1000:
            raise ValueError('Page count is too large')
        return value

class BookRead(BookBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)