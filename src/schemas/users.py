from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from schemas.profiles import ProfileBase, ProfileRead
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    age: Optional[int] = None


@field_validator('username')
@classmethod
def validate_string_filed(cls, value: Optional[str]) -> Optional[str]:
    if value is None:
        return value
    cleaned_value = value.strip()
    if not cleaned_value:
        raise ValueError('username is required')
    if len(cleaned_value) < 2:
        raise ValueError('Username must be at least 2 characters')
    return cleaned_value



@field_validator('age')
@classmethod
def validate_int(cls, value: Optional[int]) -> Optional[int]:
    if value is None:
        return value
    if value <= 0:
        raise ValueError('Age must be greater than zero')
    if value > 100:
        raise ValueError('Age is too high')
    return value


class UserCreate(UserBase):
    profile: Optional[ProfileBase] = None

class UserUpdate(UserBase):
    profile: Optional[ProfileBase] = None

class UserRead(UserBase):
    id: UUID
    profile: Optional[ProfileRead] = None

    model_config = ConfigDict(from_attributes=True)