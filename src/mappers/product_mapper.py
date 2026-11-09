from src.schemas.products import ProductRead
from src.models.product import ProductModel
from typing import Annotated
from fastapi import Depends


class ProductMapper:
    def to_read(self, product: ProductModel) -> ProductRead:
        return ProductRead.model_validate(product)

