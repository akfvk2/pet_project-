from enum import Enum
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base_model import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models.order_item import OrderItemModel


class OrderStatus(str, Enum):
    PENDING = "pending"
    CANCELLED = "cancelled"


class OrderModel(Base):
    __tablename__ = 'orders'
    status: Mapped[str] = mapped_column(sa.String(), nullable=False, default=OrderStatus.PENDING)
    items: Mapped[list["OrderItemModel"]] = relationship("OrderItemModel", back_populates="order", lazy="selectin")