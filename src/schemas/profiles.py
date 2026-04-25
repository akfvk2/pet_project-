from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID

class ProfileBase(BaseModel):
    bio: Optional[str] = None

    @field_validator('bio')
    @classmethod
    def validate_string_filed(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('Поле не может быть пустым или состоять только из пробелов')
        if len(cleaned_value) < 2:
            raise ValueError('Укажите реальныое bio')
        return cleaned_value

class ProfileRead(ProfileBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)