from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID
from src.exceptions.validation_error import ValidationException
from src.schemas.order_items import OrderItemCreate, OrderItemRead


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

    @field_validator('items')
    @classmethod
    def validate_items(cls, value: list[OrderItemCreate]) -> list[OrderItemCreate]:
        if not value:
            raise ValidationException(message='Order must contain at least one item')
        return value


class OrderRead(BaseModel):
    id: UUID
    status: str
    items: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)