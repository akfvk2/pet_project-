import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4
from src.models.base_model import Base
from datetime import datetime


class PendingConfirmationModel(Base):
    __tablename__ = 'pending_confirmations'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    reference_id: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    status: Mapped[str] = mapped_column(sa.String(), nullable=False, server_default="pending", default="pending")
    not_found_attempts: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0", default=0)
    unreachable_attempts: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0", default=0)
    next_check_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True, default=None)
    operation_type: Mapped[str] = mapped_column(sa.String(), nullable=False, server_default="order_confirmation", default="order_confirmation")