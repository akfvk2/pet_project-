import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from src.models.base_model import Base

if TYPE_CHECKING:
    from src.models.profile import ProfileModel

class UserModel(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(sa.String())
    profile: Mapped["ProfileModel"] = relationship("ProfileModel", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    email: Mapped[str] = mapped_column(sa.String())
    age: Mapped[int] = mapped_column(sa.Integer())