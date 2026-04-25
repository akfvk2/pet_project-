import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from typing import TYPE_CHECKING
from src.models.base_model import Base

if TYPE_CHECKING:
    from src.models.user import UserModel

class ProfileModel(Base):
    __tablename__ = 'profiles'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    bio: Mapped[str] = mapped_column(sa.String())
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profile")