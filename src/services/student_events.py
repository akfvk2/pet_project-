from src.repositories.outbox_event import OutboxEventRepository
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from src.schemas.student_events import StudentCreatedEvent
from src.models.outbox_event import OutboxEventModel


class StudentEventService:
    def __init__(self, session: AsyncSession):
        self.outbox_repo = OutboxEventRepository(session)

    def register_student_created(self, student) -> None:
        event_id = uuid4()
        event = StudentCreatedEvent(
            event_id=event_id,
            event="student_created",
            student_id=student.id,
            name=student.name,
        )
        payload = event.model_dump_json()
        outbox_event = OutboxEventModel(
            id=event_id,
            topic=settings.student_events_topic,
            key=str(student.id),
            payload=payload,
        )
        self.outbox_repo.register_event(outbox_event)