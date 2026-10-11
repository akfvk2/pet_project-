from uuid import uuid4
from sqlalchemy import select
from src.services.student_events import StudentEventService
from src.services.outbox_service import OutboxService
from src.repositories.outbox_event import OutboxEventRepository
from src.models.outbox_event import OutboxEventModel
from src.models.student import Students
from src.config import settings


async def test_register_student_created_writes_outbox_event(db_session):
    student = Students(id=uuid4(), name="Ivan", age=20, email="ivan@test.com", phone="+79990000000")
    service = StudentEventService(OutboxService(OutboxEventRepository(db_session)))

    service.register_student_created(student)
    await db_session.commit()

    result = await db_session.execute(select(OutboxEventModel).where(OutboxEventModel.key == str(student.id)))
    row = result.scalar_one()
    assert row.topic == settings.student_events_topic
    assert "student_created" in row.payload
    assert student.name in row.payload
