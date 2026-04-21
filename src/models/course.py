import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from src.models.base_model import Base
from src.models.student import Students

class Course(Base):
    __tablename__ = 'courses'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(sa.String())
    description: Mapped[str] = mapped_column(sa.String())
    duration_hours: Mapped[int] = mapped_column(sa.Integer())
    students: Mapped[list["Students"]] = relationship("Students", back_populates="course")