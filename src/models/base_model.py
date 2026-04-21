from datetime import datetime
from typing import Optional
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column, relationship
from uuid import UUID, uuid4

metadata = sa.MetaData()


class BaseServiceModel:
    """Базовый класс для таблиц сервиса."""

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None


Base: DeclarativeMeta = declarative_base(metadata=metadata, cls=BaseServiceModel)



class UserModel(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(sa.String())
    profile: Mapped["ProfileModel"] = relationship(back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    email: Mapped[str] = mapped_column(sa.String())
    age: Mapped[int] = mapped_column(sa.Integer())

class ProfileModel(Base):
    __tablename__ = 'profiles'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    bio: Mapped[str] = mapped_column(sa.String())
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profile")

class Author(Base):
    __tablename__ = 'authors'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String())
    biography: Mapped[str] = mapped_column(sa.String())
    birth_date: Mapped[datetime] = mapped_column(sa.DateTime())
    nationality: Mapped[str] = mapped_column(sa.String())
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author", cascade="all, delete-orphan", lazy="selectin")

class Book(Base):
    __tablename__ = 'books'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(sa.String())
    page_count: Mapped[int] = mapped_column(sa.Integer())
    genre: Mapped[str] = mapped_column(sa.String())
    author_id: Mapped[UUID] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    author: Mapped["Author"] = relationship("Author", back_populates="books")

class Students(Base):
    __tablename__ = 'students'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String())
    age: Mapped[int] = mapped_column(sa.Integer())
    email: Mapped[str] = mapped_column(sa.String())
    phone: Mapped[str] = mapped_column(sa.String())
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=True) 
    course: Mapped["Course"] = relationship("Course", back_populates='students', lazy="selectin")

class Course(Base):
    __tablename__ = 'courses'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(sa.String())
    description: Mapped[str] = mapped_column(sa.String())
    duration_hours: Mapped[int] = mapped_column(sa.Integer())
    students: Mapped[list["Students"]] = relationship("Students", back_populates="course")
