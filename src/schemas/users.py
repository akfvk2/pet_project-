import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from schemas.profiles import ProfileBase, ProfileRead
from uuid import UUID
from src.exceptions.validation_error import ValidationException



class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    age: Optional[int] = None

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: Optional[EmailStr]) -> Optional[EmailStr]:
        if value is None:
            return value
        cleaned_email = value.strip()
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_regex.match(cleaned_email):
            raise ValidationException(message="Invalid email format")
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

    def to_model(self):
        from src.models.user import UserModel
        from src.models.profile import ProfileModel
        user_data = self.model_dump(exclude={"profile"})
        user_entity = UserModel(**user_data)
        if self.profile is not None:
            profile_entity = ProfileModel(**self.profile.model_dump())
            user_entity.profile = profile_entity
        return user_entity

class UserUpdate(UserBase):
    profile: Optional[ProfileBase] = None

    @field_validator('profile')
    @classmethod
    def validate_profile_ext(cls, value):
        if value is not None and not value.bio.strip():
            raise ValidationException(message="If profile is provided, bio cannot be empty")
        return value

    def update_model(self, user_entity):
        from src.models.profile import ProfileModel
        updated_data = self.model_dump(exclude_unset=True, exclude={"profile"})
        if self.profile is not None:
            profile_data = self.profile.model_dump(exclude_unset=True)
            if user_entity.profile:
                for p_key, p_value in profile_data.items():
                    setattr(user_entity.profile, p_key, p_value)
            else:
                user_entity.profile = ProfileModel(**profile_data)
        for key, value in updated_data.items():
            setattr(user_entity, key, value)
        return user_entity


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