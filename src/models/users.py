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
    profile = Mapped["ProfileModel"] = relationship(back_populates="Profiles", cascade="all, delete-orphan")

class ProfileModel(Base):
    __tablename__ = 'profiles'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    bio: Mapped[str] = mapped_column(sa.String())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    users: Mapped["UserModel"] = relationship("UserModel", back_populates="profiles")

class Author(Base):
    __tablename__ = 'authors'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    name: Mapped[str] = mapped_column(sa.String())
    books: Mapped["Book"] = relationship("Book", back_populates="authors", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = 'books'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    title: Mapped[str] = mapped_column(sa.String())
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    author: Mapped["Author"] = relationship("Author", back_populates="books")

class Students(Base):
    __tablename__ = 'students'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    name: Mapped[str] = mapped_column(sa.String())
    course: Mapped["Course"] = relationship("Course", back_populates='students', cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = 'courses'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())
    title: Mapped[str] = mapped_column(sa.String())
    students: Mapped["Students"] = relationship("Student", back_populates="course")
