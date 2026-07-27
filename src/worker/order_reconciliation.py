import asyncio
import logging
from uuid import UUID

from src.db import SessionFactory
from src.config import settings
from src.repositories.pending_order_confirmation import PendingOrderConfirmationRepository, PENDING, NEEDS_REVIEW
from src.clients.order_client import OrderServiceClient
from src.exceptions.service_exception import ServiceException

logger = logging.getLogger(__name__)
_order_client = OrderServiceClient()
_repo: PendingOrderConfirmationRepository | None = None

def _get_repo(session) -> PendingOrderConfirmationRepository:
    global _repo
    if _repo is None:
        _repo = PendingOrderConfirmationRepository(session)
    else:
        _repo.session = session
    return _repo

async def _claim_batch(batch_size: int = 20):
    async with SessionFactory() as session:
        repo = _get_repo(session)
        claimed = await repo.claim_batch(batch_size)
        await session.commit()
        return claimed


async def _process_row(row_id: UUID) -> None:
    async with SessionFactory() as session:
        repo = _get_repo(session)
        row = await repo.get_by_id(row_id)
        if row is None:
            return
        user_id, reference_id = row.user_id, row.reference_id

    try:
        existing_orders = await _order_client.get_orders_by_user_id(user_id)
        existing_order = next((o for o in existing_orders if o.reference_id == reference_id), None)
        outcome = "found" if existing_order else "not_found"
    except ServiceException:
        outcome = "unreachable"
    except Exception:
        logger.exception(f"Reconciliation: unexpected error checking user {user_id}")
        raise
    async with SessionFactory() as session:
        repo = _get_repo(session)
        row = await repo.get_by_id(row_id)
        if row is None:
            return
        try:
            if outcome == "found":
                await repo.delete(row)
            elif outcome == "not_found":
                row.attempts += 1
                if row.attempts >= settings.reconciliation_max_attempts:
                    logger.error(
                        f"Reconciliation: order genuinely not found for user {row.user_id} after {row.attempts} checks — needs manual review"
                    )
                    row.status = NEEDS_REVIEW
                else:
                    row.status = PENDING
            else:
                row.attempts += 1
                if row.attempts >= settings.reconciliation_max_attempts:
                    logger.error(
                        f"Reconciliation: user {row.user_id} still has no confirmed order after {row.attempts} checks — needs manual review"
                    )
                    row.status = NEEDS_REVIEW
                else:
                    row.status = PENDING
            await session.commit()
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