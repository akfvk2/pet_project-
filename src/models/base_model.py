import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeMeta, Mapped, declarative_base, mapped_column, relationship
from datetime import datetime
from sqlalchemy import DateTime, func


metadata = sa.MetaData()


class BaseServiceModel:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    """Базовый класс для таблиц сервиса."""

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None


Base: DeclarativeMeta = declarative_base(metadata=metadata, cls=BaseServiceModel)



