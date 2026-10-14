from enum import Enum
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from src.models.base_model import Base

if TYPE_CHECKING:
    from src.models.booking import BookingModel


class RoomModel(Base):
    __tablename__ = 'rooms'
    roomname: Mapped[str] = mapped_column(sa.String())
    reservation: Mapped[list["BookingModel"]] = relationship("BookingModel", back_populates='room', lazy="selectin")
