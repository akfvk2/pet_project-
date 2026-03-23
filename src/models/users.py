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
    
    # Correct back_populates to match the attribute name in ProfileModel ("user")
    profile: Mapped["ProfileModel"] = relationship(back_populates="user", cascade="all, delete-orphan")

class ProfileModel(Base):
    __tablename__ = 'profiles'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    bio: Mapped[str] = mapped_column(sa.String())
    
    # Needs to be UUID to match users.id
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    # Attribute name "user" (singular) makes sense for One-to-One
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profile")

class Author(Base):
    __tablename__ = 'authors'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String())
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = 'books'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(sa.String())
    
    # Needs to be UUID to match authors.id
    author_id: Mapped[UUID] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    author: Mapped["Author"] = relationship("Author", back_populates="books")

class Students(Base):
    __tablename__ = 'students'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String())
    
    # Add course_id foreign key
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=True) 
    course: Mapped["Course"] = relationship("Course", back_populates='students')

class Course(Base):
    __tablename__ = 'courses'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(sa.String())
    
    # Relationship target should correspond to class name "Students"
    students: Mapped[list["Students"]] = relationship("Students", back_populates="course")
