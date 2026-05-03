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
            return None
        if len(cleaned_value) < 2:
            raise ValueError('Bio must be at least 2 characters')
        return cleaned_value

class ProfileRead(ProfileBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)