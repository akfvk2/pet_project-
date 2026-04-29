from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_hours: Optional[int] = None

    @field_validator('title')
    @classmethod
    def validate_string_field(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('Title cannot be empty')
        if len(cleaned_value) < 2:
            raise ValueError('Title is required')
        return cleaned_value

    @field_validator( 'description')
    @classmethod
    def validate_string_field_op(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_value = value.strip()
        if len(cleaned_value) < 2:
            raise ValueError('Description must be at least 2 characters')
        return cleaned_value

    @field_validator('duration_hours')
    @classmethod
    def validate_int(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value <= 0:
            raise ValueError('Duration must be greater than zero')
        if value > 500:
            raise ValueError('Duration cannot exceed 500 hours')
        return value

class CourseRead(CourseBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

