from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    bio: Optional[str] = None


class ProfileRead(ProfileBase):
    id: int

    model_config = ConfigDict(from_attributes=True)