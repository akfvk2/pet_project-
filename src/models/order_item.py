import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from src.models.base_model import Base
from typing import TYPE_CHECKING
from decimal import Decimal


if TYPE_CHECKING:
    from src.models.order import OrderModel


class OrderItemModel(Base):
    __tablename__ = 'order_items'
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(sa.Integer())
    price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2))
    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="items", lazy="noload")