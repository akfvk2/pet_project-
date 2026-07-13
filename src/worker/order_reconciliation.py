import asyncio
import logging
from uuid import UUID

from src.db import SessionFactory
from src.config import settings
from src.repositories.pending_order_confirmation import PendingOrderConfirmationRepository, PENDING, NEEDS_REVIEW
from src.clients.order_client import OrderServiceClient
from src.exceptions.service_exception import ServiceException

logger = logging.getLogger(__name__)


async def _claim_batch(batch_size: int = 20):
    async with SessionFactory() as session:
        repo = PendingOrderConfirmationRepository(session)
        claimed = await repo.claim_batch(batch_size)
        await session.commit()
        return claimed


async def _process_row(row_id: UUID) -> None:
    order_client = OrderServiceClient()
    async with SessionFactory() as session:
        repo = PendingOrderConfirmationRepository(session)
        row = await repo.get_by_id(row_id)
        if row is None:
            return

        try:
            existing_order = await order_client.get_order_by_reference_id(row.user_id, row.reference_id)
        except ServiceException:
            logger.warning(f"Reconciliation: order service still unreachable for user {row.user_id}")
            row.attempts += 1
            row.status = PENDING
            await session.commit()
            return
        except Exception:
            logger.exception(f"Reconciliation: unexpected error checking user {row.user_id}")
            row.status = PENDING
            await session.commit()
            return

        if existing_order:
            await repo.delete(row)
            await session.commit()
            return

        row.attempts += 1
        if row.attempts >= settings.reconciliation_max_attempts:
            logger.critical(
                f"Reconciliation: user {row.user_id} still has no confirmed order after {row.attempts} checks — needs manual review"
            )
            row.status = NEEDS_REVIEW
        else:
            row.status = PENDING
        await session.commit()


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