from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from pydantic.v1 import Field
from src.exceptions.validation_error import ValidationException
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
    def validate_name(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValidationException(message='name cannot be empty')
        if len(cleaned_value) < 2:
            raise ValidationException(message='Name must be at least 2 characters')
        return cleaned_value

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned_phone = re.sub(r'[\s\-()]', '', value)
        if not re.match(r'^\+?\d{9,15}$', cleaned_phone):
            raise ValidationException(message="Enter the phone number in the format +79999999999")
        return cleaned_phone

    @field_validator('age')
    @classmethod
    def validate_age(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value <= 0:
            raise ValidationException(message='Age must be greater than zero')
        if value > 100:
            raise ValidationException(message='Age is too high')
        return value

class StudentCreate(StudentBase):
    course: UUID = Field(min_length=1)

    def to_model(self):
        from src.models.student import Students
        data = self.model_dump(exclude={"course"})
        entity = Students(**data, course_id=self.course)
        return entity

class StudentUpdate(StudentBase):
    course: Optional[UUID] = None

    def update_model(self, student_entity):
        update_data = self.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(student_entity, key, value)
        return student_entity

class StudentRead(StudentBase):
    id: UUID
    course: Optional[CourseRead] = None

    model_config = ConfigDict(from_attributes=True)