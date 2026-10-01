from enum import Enum
from pydantic import BaseModel
from uuid import UUID

class StudentEventType(str, Enum):
    STUDENT_CREATED = "student_created"

class StudentCreatedEvent(BaseModel):
    event_id: UUID
    event: str
    student_id: UUID
    name: str

