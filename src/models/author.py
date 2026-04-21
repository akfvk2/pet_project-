from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from src.models.base_model import Base
from src.models.book import Book


class Author(Base):
    __tablename__ = 'authors'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String())
    biography: Mapped[str] = mapped_column(sa.String())
    birth_date: Mapped[datetime] = mapped_column(sa.DateTime())
    nationality: Mapped[str] = mapped_column(sa.String())
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author", cascade="all, delete-orphan", lazy="selectin")