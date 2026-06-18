from pydantic import BaseModel, field_validator
from uuid import UUID
from src.exceptions.validation_error import ValidationException




class OrderCreate(BaseModel):
    title: str
    price: float
    description: str = ""

    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValidationException(message='Title is required')
        if len(value.strip()) < 2:
            raise ValidationException(message='Title must be at least 2 characters')
        return value.strip()

    @field_validator('price')
    @classmethod
    def validate_price(cls, value: float) -> float:
        if value <= 0:
            raise ValidationException(message='Price must be greater than 0')
        return value

    @field_validator('description')
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()
        if len(value) > 500:
            raise ValidationException(message='Description must be at most 500 characters')
        return value

class OrderCreateRequest(OrderCreate):
    user_id: UUID



class OrderResponse(BaseModel):
    id: UUID
    title: str
    price: float
    description: str
    status: str
