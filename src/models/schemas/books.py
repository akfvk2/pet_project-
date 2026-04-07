from typing import Optional
from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str
    page_count: Optional[int] = None
    genre: Optional[str] = None


class BookRead(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)