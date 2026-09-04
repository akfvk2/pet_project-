from pydantic import BaseModel
from uuid import UUID


class StudentCreatedEvent(BaseModel):
    event_id: UUID
    event: str
    student_id: UUID
    name: str

