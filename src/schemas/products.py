from pydantic import BaseModel, ConfigDict, field_validator
from src.models.product import ProductModel
from uuid import UUID, uuid4
from src.exceptions.validation_error import ValidationException


class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        if len(value) > 20:
            raise ValidationException(message='name must be less than 20 characters')
        return value

    @field_validator('price')
    @classmethod
    def validate_price(cls, value):
        if value <= 0:
            raise ValidationException(message='price must be greater than 0')
        return value

    @field_validator('stock')
    @classmethod
    def validate_stock(cls, value):
        if value <= 0:
            raise ValidationException(message='stock must be greater than 0')
        return value

    def to_model(self) -> ProductModel:
        return ProductModel(id=uuid4(), **self.model_dump())


class ProductRead(ProductCreate):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    stock: int | None = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        if value is None:
            return value
        if len(value) > 20:
            raise ValidationException(message='name must be less than 20 characters')
        return value

    @field_validator('price')
    @classmethod
    def validate_price(cls, value):
        if value is None:
            return value
        if value <= 0:
            raise ValidationException(message='price must be greater than 0')
        return value

    @field_validator('stock')
    @classmethod
    def validate_stock(cls, value):
        if value is None:
            return value
        if value <= 0:
            raise ValidationException(message='stock must be greater than 0')
        return value

    def update_model(self, product_entity: ProductModel) -> ProductModel:
        for key, value in self.model_dump(exclude_unset=True).items():
            setattr(product_entity, key, value)
        return product_entity

