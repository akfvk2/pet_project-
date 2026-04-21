from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, ValidationError
from schemas.profiles import ProfileBase, ProfileRead
from uuid import UUID


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    age: Optional[int] = None

@field_validator('username', 'email')
@classmethod
def validate_string_filed(cls, value: Optional[str]) -> Optional[str]:
    if value is None:
        return value
    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValueError('username or email is required')
    if len(cleaned_value) < 2:
        raise ValueError('username or email is required')
    return cleaned_value

@field_validator('age')
@classmethod
def validate_int(cls, value: Optional[int]) -> Optional[int]:
    if value is None:
        return value
    if value <= 0:
        raise ValueError('Возраст должен быть больше нуля')
    if value > 100:
        raise ValueError('Укажите реальный возраст')
    return value


class UserCreate(UserBase):
    profile: Optional[ProfileBase] = None

class UserUpdate(UserBase):
    profile: Optional[ProfileBase] = None

class UserRead(UserBase):
    id: UUID
    profile: Optional[ProfileRead] = None

    model_config = ConfigDict(from_attributes=True)