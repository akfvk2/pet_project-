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
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    username: Mapped[str] = mapped_column(sa.String())
    profile: Mapped[Optional["ProfileModel"]] = relationship(
        "ProfileModel",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

class ProfileModel(Base):
    __tablename__ = 'profiles'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    bio: Mapped[str] = mapped_column(sa.String())
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profile")

class Author(Base):
    __tablename__ = 'authors'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    name: Mapped[str] = mapped_column(sa.String())
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = 'books'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    title: Mapped[str] = mapped_column(sa.String())
    author_id: Mapped[UUID] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    author: Mapped["Author"] = relationship("Author", back_populates="books")

class Students(Base):
    __tablename__ = 'students'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    name: Mapped[str] = mapped_column(sa.String())
    course: Mapped[list["Course"]] = relationship("Course", back_populates='students', cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = 'courses'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    title: Mapped[str] = mapped_column(sa.String())
    students: Mapped[list["Students"]] = relationship("Students", back_populates="course")
