from datetime import datetime
from enum import Enum
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from src.models.base_model import Base
from src.models.room import RoomModel
from src.models.user import UserModel


class BookingStatus(str, Enum):
    Active = "active"
    Cancelled = "cancelled"

class BookingModel(Base):
    __tablename__ = 'booking'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    starts_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    status: Mapped[str] = mapped_column(sa.String(), nullable=False,server_default=BookingStatus.Active.value,default=BookingStatus.Active)
    room: Mapped["RoomModel"] = relationship("RoomModel", back_populates='reservation', lazy="noload")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="booking", lazy="noload")