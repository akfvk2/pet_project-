from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID

class BookBase(BaseModel):
    title: str
    page_count: Optional[int] = None
    genre: Optional[str] = None

    @field_validator('title', 'genre')
    @classmethod
    def validate_string_filed(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('username or email or phone is required')
        if len(cleaned_value) < 2:
            raise ValueError('username or email or phone is required')
        return cleaned_value

    @field_validator('page_count')
    @classmethod
    def validate_int(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value <= 0:
            raise ValueError('Продолжительность должена быть больше нуля')
        if value > 100:
            raise ValueError('Укажите реальную продолжительность')
        return value

class BookRead(BookBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)