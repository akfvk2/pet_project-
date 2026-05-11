import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from schemas.profiles import ProfileBase, ProfileRead
from uuid import UUID
from src.exceptions.validation_error import ValidationException



class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    age: Optional[int] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_email = value.strip()
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.match(cleaned_email):
            raise ValidationException(message="Invalid format email")
        return cleaned_email

    @field_validator('username')
    @classmethod
    def validate_username(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValidationException(message='username is required')
        if len(cleaned_value) < 2:
            raise ValidationException(message='Username must be at least 2 characters')
        return cleaned_value




    @field_validator('age')
    @classmethod
    def validate_age(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value <= 0:
            raise ValidationException(message='Age must be greater than zero')
        if value > 100:
            raise ValidationException(message='Age is too high')
        return value


class UserCreate(UserBase):
    profile: Optional[ProfileBase] = None

    @field_validator('profile')
    @classmethod
    def validate_profile_ext(cls, value):
        if value is not None and not value.bio.strip():
            raise ValidationException(message="If profile is provided, bio cannot be empty")
        return value

class UserUpdate(UserBase):
    profile: Optional[ProfileBase] = None

    @field_validator('profile')
    @classmethod
    def validate_profile_ext(cls, value):
        if value is not None and not value.bio.strip():
            raise ValidationException(message="If profile is provided, bio cannot be empty")
        return value


class UserRead(UserBase):
    id: UUID
    profile: Optional[ProfileRead] = None

    @field_validator('profile')
    @classmethod
    def validate_profile_ext(cls, value):
        if value is not None and not value.bio.strip():
            raise ValidationException(message="If profile is provided, bio cannot be empty")
        return value

    model_config = ConfigDict(from_attributes=True)