from typing import Optional
from pydantic import BaseModel, ConfigDict



class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_hours: Optional[int] = None


class CourseRead(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

