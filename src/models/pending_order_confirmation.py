import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4
from src.models.base_model import Base



class PendingOrderConfirmationModel(Base):
    __tablename__ = 'pending_order_confirmations'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    attempts: Mapped[int] = mapped_column(sa.Integer(), default=0)