from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from src.exceptions.validation_error import ValidationException
from schemas.courses import CourseRead, CourseUpdate
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

    def to_model(self):
        data = self.model_dump(exclude={"course"})
        entity = Students(**data)
        if self.course:
            entity.course = Course(**self.course.model_dump())
        return entity

class StudentUpdate(StudentBase):
    course: Optional[CourseUpdate] = None

    def update_model(self, student_entity):
        student_update_data = self.model_dump(exclude={"course"}, exclude_unset=True)
        for key, value in student_update_data.items():
            setattr(student_entity, key, value)
        if self.course is not None:
            if student_entity.course:
                course_data = self.course.model_dump(exclude_unset=True)
                for key, value in course_data.items():
                    setattr(student_entity.course, key, value)
            else:
                from src.models.course import Course
                student_entity.course = Course(**self.course.model_dump())
        return student_entity

class StudentRead(StudentBase):
    id: UUID
    course: Optional[CourseRead] = None

    model_config = ConfigDict(from_attributes=True)