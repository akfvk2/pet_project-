from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID
from src.exceptions.validation_error import ValidationException


class ProfileBase(BaseModel):
    bio: Optional[str] = None

    @field_validator('bio')
    @classmethod
    def validate_bio(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            return None
        if len(cleaned_value) < 2:
            raise ValidationException(message='Bio must be at least 2 characters')
        if len(cleaned_value) > 300:
            raise ValidationException(message='Bio must be less than 300 characters')
        return cleaned_value

class ProfileRead(ProfileBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)