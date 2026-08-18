import pytest_asyncio
from uuid import uuid4
from src.repositories.pending_confirmation import PendingConfirmationRepository, PendingConfirmationStatus
from src.models.pending_confirmation import PendingConfirmationModel
from src.models.user import UserModel
from src.repositories.user import UserRepository


@pytest_asyncio.fixture
async def repo(db_session):
    return PendingConfirmationRepository(db_session)


class TestPendingConfirmationRepository:
    async def test_claim_batch_sets_updated_at(self, repo, db_session):
        user_repo = UserRepository(db_session)
        user = await user_repo.create(UserModel(username="testuser", email="test@gmail.com", age=25))

        pending = PendingConfirmationModel(user_id=user.id, reference_id=uuid4())
        db_session.add(pending)
        await db_session.commit()
        await db_session.refresh(pending)

        assert pending.updated_at is None  # onupdate не срабатывает на INSERT

        claimed = await repo.claim_batch()
        await db_session.commit()

        assert len(claimed) == 1
        assert claimed[0].status == PendingConfirmationStatus.IN_PROGRESS
        assert claimed[0].updated_at is not None

    async def test_claim_batch_does_not_reclaim_immediately(self, repo, db_session):
        user_repo = UserRepository(db_session)
        user = await user_repo.create(UserModel(username="testuser2", email="test2@gmail.com", age=25))

        pending = PendingConfirmationModel(user_id=user.id, reference_id=uuid4())
        db_session.add(pending)
        await db_session.commit()

        first_claim = await repo.claim_batch()
        await db_session.commit()
        assert len(first_claim) == 1

        second_claim = await repo.claim_batch()
        await db_session.commit()
        assert second_claim == []