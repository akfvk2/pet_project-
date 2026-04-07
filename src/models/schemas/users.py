from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.models.schemas.profiles import ProfileBase, ProfileRead


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    age: Optional[int] = None



class UserCreate(UserBase):
    profile: Optional[ProfileBase] = None


class UserUpdate(UserBase):
    profile: Optional[ProfileBase] = None


class UserRead(UserBase):
    id: int
    profile: Optional[ProfileRead] = None

    model_config = ConfigDict(from_attributes=True)