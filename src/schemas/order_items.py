from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID
from src.exceptions.validation_error import ValidationException


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if value <= 0:
            raise ValidationException(message='Quantity must be greater than 0')
        return value


class OrderItemRead(BaseModel):
    product_id: UUID
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)