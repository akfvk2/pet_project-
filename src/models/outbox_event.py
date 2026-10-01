import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4
from src.models.base_model import Base
from enum import Enum
from datetime import datetime

class OutboxEventStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PUBLISHED = "published"
    FAILED = "failed"



class OutboxEventModel(Base):
    __tablename__ = 'outbox_events'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    topic: Mapped[str] = mapped_column(sa.String(), nullable=False)
    key: Mapped[str] = mapped_column(sa.String(), nullable=False)
    payload: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(), nullable=False, server_default=OutboxEventStatus.PENDING.value, default=OutboxEventStatus.PENDING)
    attempts: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0", default=0)
    version: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0", default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True, default=None)
    stale_attempt: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default="0", default=0)
    last_error: Mapped[str | None] = mapped_column(sa.Text(), nullable=True, default=None)