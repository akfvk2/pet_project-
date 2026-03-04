from typing import Optional, List
from pydantic import BaseModel

#User/Profile

class ProfileBase(BaseModel):
    bio: Optional[str] = None

class ProfileRead(ProfileBase):
    id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    profile: Optional[ProfileBase] = None


class UserUpdate(UserBase):
    profile: Optional[ProfileBase] = None


class UserRead(UserBase):
    id: int
    profile: Optional[ProfileRead] = None

    class Config:
        orm_mode = True

# Author/Book

class BookBase(BaseModel):
    title: str


class BookRead(BookBase):
    id: int

    class Config:
        orm_mode = True


class AuthorBase(BaseModel):
    name: str


class AuthorCreate(AuthorBase):
    books: Optional[List[BookBase]] = None


class AuthorUpdate(AuthorBase):
    books: Optional[List[BookBase]] = None


class AuthorRead(AuthorBase):
    id: int
    books: List[BookRead] = None

    class Config:
        orm_mode = True

# Student/Course

class CourseBase(BaseModel):
    title: str


class CourseRead(CourseBase):
    id: int

    class Config:
        orm_mode = True


class StudentBase(BaseModel):
    name: str


class StudentCreate(StudentBase):
    courses: Optional[List[int]] = None


class StudentUpdate(StudentBase):
    courses: Optional[List[int]] = None


class StudentRead(StudentBase):
    id: int
    courses: List[CourseRead] = None

    class Config:
        orm_mode = True


