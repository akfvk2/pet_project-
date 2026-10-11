import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from src.models.base_model import Base


if TYPE_CHECKING:
    from src.models.course import Course

class Students(Base):
    __tablename__ = 'students'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(sa.String())
    age: Mapped[int] = mapped_column(sa.Integer())
    email: Mapped[str] = mapped_column(sa.String())
    phone: Mapped[str] = mapped_column(sa.String())
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    course: Mapped["Course"] = relationship("Course", back_populates='students', lazy="selectin")