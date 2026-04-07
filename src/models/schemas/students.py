from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from src.models.schemas.courses import CourseRead

class StudentBase(BaseModel):
    name: str
    age: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class StudentCreate(StudentBase):
    courses: Optional[List[int]] = None


class StudentUpdate(StudentBase):
    courses: Optional[List[int]] = None


class StudentRead(StudentBase):
    id: int
    courses: List[CourseRead] = None

    model_config = ConfigDict(from_attributes=True)