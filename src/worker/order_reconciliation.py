import asyncio
import logging
from uuid import UUID
from contextlib import asynccontextmanager
from src.db import SessionFactory
from src.config import settings
from src.repositories.pending_order_confirmation import PendingOrderConfirmationRepository, PendingOrderConfirmationStatus
from src.clients.order_client import OrderServiceClient
from src.exceptions.service_exception import ServiceException
from enum import Enum


logger = logging.getLogger(__name__)
_order_client = OrderServiceClient()

class ReconciliationOutcome(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    UNREACHABLE = "unreachable"

@asynccontextmanager
async def _repo_session():
    async with SessionFactory() as session:
        yield PendingOrderConfirmationRepository(session)

async def _claim_batch(batch_size: int = 20):
    async with _repo_session() as repo:
        return await repo.claim_batch(batch_size)

async def _apply_outcome(repo: PendingOrderConfirmationRepository, row, outcome: ReconciliationOutcome) -> None:
    if outcome == ReconciliationOutcome.FOUND:
        await repo.delete(row)
        return
    row.attempts += 1
    if outcome == ReconciliationOutcome.NOT_FOUND and row.attempts >= settings.reconciliation_max_attempts:
        logger.error(
            f"Reconciliation: order genuinely not found for user {row.user_id} after {row.attempts} checks — needs manual review"
        )
        row.status = PendingOrderConfirmationStatus.NEEDS_REVIEW
    else:
        row.status = PendingOrderConfirmationStatus.PENDING

async def _process_row(row_id: UUID) -> None:
    async with _repo_session() as repo:
        row = await repo.get_by_id(row_id)
        if row is None:
            return
        user_id, reference_id = row.user_id, row.reference_id

    try:
        existing_orders = await _order_client.get_orders_by_user_id(user_id)
        existing_order = next((o for o in existing_orders if o.reference_id == reference_id), None)
        outcome = ReconciliationOutcome.FOUND if existing_order else ReconciliationOutcome.NOT_FOUND
    except ServiceException:
        outcome = ReconciliationOutcome.UNREACHABLE
    except Exception:
        logger.exception(f"Reconciliation: unexpected error checking user {user_id}")
        raise
    async with _repo_session() as repo:
        row = await repo.get_by_id(row_id)
        if row is None:
            return
        try:
            await _apply_outcome(repo, row, outcome)
            await repo.session.commit()
        except Exception:
            logger.exception(f"Reconciliation: failed to persist result for row {row_id}")
            raise


async def _reconcile_once() -> None:
    claimed = await _claim_batch()
    for row in claimed:
        await _process_row(row.id)


async def run_reconciliation_worker() -> None:
    while True:
        try:
            await _reconcile_once()
        except Exception:
            logger.exception("Reconciliation worker iteration failed")
        await asyncio.sleep(settings.reconciliation_interval_seconds)