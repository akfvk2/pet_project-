import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base_model import Base


class ProductModel(Base):
    __tablename__ = 'products'
    name: Mapped[str] = mapped_column(sa.String())
    price: Mapped[float] = mapped_column(sa.Numeric(10, 2))
    stock: Mapped[int] = mapped_column(sa.Integer(), nullable=False, default=0)
