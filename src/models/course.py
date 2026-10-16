import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from src.models.base_model import Base

if TYPE_CHECKING:
    from src.models.student import Students

class Course(Base):
    __tablename__ = 'courses'
    title: Mapped[str] = mapped_column(sa.String())
    description: Mapped[str] = mapped_column(sa.String())
    duration_hours: Mapped[int] = mapped_column(sa.Integer())
    students: Mapped[list["Students"]] = relationship("Students", back_populates="course")