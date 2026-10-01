from uuid import uuid4
from src.repositories.outbox_event import OutboxEventRepository
from src.models.outbox_event import OutboxEventModel

class OutboxService:
    def __init__(self, outbox_repo: OutboxEventRepository):
        self.outbox_repo = outbox_repo

    def register(self, topic: str, key: str, payload: str) -> None:
        outbox_event = OutboxEventModel(id=uuid4(), topic=topic, key=key, payload=payload)
        self.outbox_repo.register_event(outbox_event)