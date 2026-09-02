import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from src.models.base_model import Base

if TYPE_CHECKING:
    from src.models.author import Author

class Book(Base):
    __tablename__ = 'books'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(sa.String())
    page_count: Mapped[int] = mapped_column(sa.Integer())
    genre: Mapped[str] = mapped_column(sa.String())
    author_id: Mapped[UUID] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    author: Mapped["Author"] = relationship("Author", back_populates="books", lazy="noload")