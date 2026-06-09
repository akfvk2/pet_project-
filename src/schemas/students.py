from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from src.exceptions.validation_error import ValidationException
from src.schemas.courses import CourseRead, CourseUpdate
from uuid import UUID
import re
from src.schemas.courses import CourseCreate
from src.models.course import Course
from src.models.student import Students


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
    course: CourseCreate

    @field_validator('course')
    @classmethod
    def validate_course(cls, value):
        if value is None:
            raise ValidationException(message="Course is required")
        return value

    def to_model(self):
        data = self.model_dump(exclude={"course"})
        entity = Students(**data)
        entity.course = Course(**self.course.model_dump())
        return entity

class StudentUpdate(StudentBase):
    course: CourseUpdate

    @field_validator('course')
    @classmethod
    def validate_course(cls, value):
        if value is None:
            raise ValidationException(message="Course is required")
        return value

    def update_model(self, student_entity):
        student_update_data = self.model_dump(exclude={"course"})  # БЕЗ exclude_unset
        for key, value in student_update_data.items():
            setattr(student_entity, key, value)
        student_entity.course = Course(**self.course.model_dump())
        return student_entity

class StudentRead(StudentBase):
    id: UUID
    course: Optional[CourseRead] = None

    model_config = ConfigDict(from_attributes=True)