from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProfileBase(BaseModel):
    bio: Optional[str] = None

class ProfileRead(ProfileBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    profile: Optional[ProfileBase] = None


class UserUpdate(UserBase):
    profile: Optional[ProfileBase] = None


class UserRead(UserBase):
    id: int
    profile: Optional[ProfileRead] = None

    model_config = ConfigDict(from_attributes=True)