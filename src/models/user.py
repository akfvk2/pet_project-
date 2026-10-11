import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from src.models.base_model import Base
from src.models.room import RoomModel

if TYPE_CHECKING:
    from src.models.profile import ProfileModel
    from src.models.booking import BookingModel

class UserModel(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(sa.String())
    profile: Mapped["ProfileModel"] = relationship("ProfileModel", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    email: Mapped[str] = mapped_column(sa.String())
    age: Mapped[int] = mapped_column(sa.Integer())
    booking: Mapped[list["BookingModel"]] = relationship("BookingModel", back_populates="user", lazy="selectin")
