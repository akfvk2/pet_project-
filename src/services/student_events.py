from src.services.outbox_service import OutboxService
from uuid import uuid4
from src.config import settings
from src.schemas.student_events import StudentCreatedEvent, StudentEventType
from src.models.student import Students


class StudentEventService:
    def __init__(self, outbox_service: OutboxService):
        self.outbox_service = outbox_service

    def register_student_created(self, student: Students) -> None:
        event = StudentCreatedEvent(
            event_id=uuid4(),
            event=StudentEventType.STUDENT_CREATED.value,
            student_id=student.id,
            name=student.name,
        )
        self.outbox_service.register(
            topic=settings.student_events_topic,
            key=str(student.id),
            payload=event.model_dump_json(),
        )
