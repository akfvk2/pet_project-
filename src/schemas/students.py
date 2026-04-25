from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from schemas.courses import CourseRead
from uuid import UUID
import re

class StudentBase(BaseModel):
    name: str
    age: Optional[int] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_string_filed(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError('Поле не может быть пустым или состоять только из пробелов')
        if len(cleaned_value) < 2:
            raise ValueError('Укажите реальное имя')
        return cleaned_value

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_phone = re.sub(r'[\s\-()]', '', value)
        if not re.match(r'^\+?\d{9,15}$', cleaned_phone):
            raise ValueError("Неверный формат номера телефона")
        return cleaned_phone

    @field_validator('age')
    @classmethod
    def validate_int(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value <= 0:
            raise ValueError('Возраст должен быть больше нуля')
        if value > 100:
            raise ValueError('Укажите реальный возраст')
        return value

class StudentCreate(StudentBase):
    courses: Optional[List[UUID]] = None

class StudentUpdate(StudentBase):
    courses: Optional[List[UUID]] = None

class StudentRead(StudentBase):
    id: UUID
    courses: List[CourseRead] = None

    model_config = ConfigDict(from_attributes=True)