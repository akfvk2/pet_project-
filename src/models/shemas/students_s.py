from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class CourseBase(BaseModel):
    title: str


class CourseRead(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudentBase(BaseModel):
    name: str


class StudentCreate(StudentBase):
    courses: Optional[List[int]] = None


class StudentUpdate(StudentBase):
    courses: Optional[List[int]] = None


class StudentRead(StudentBase):
    id: int
    courses: List[CourseRead] = None

    model_config = ConfigDict(from_attributes=True)