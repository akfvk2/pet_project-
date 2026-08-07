import asyncio
import logging
from uuid import UUID
from src.db import SessionFactory
from src.config import settings
from src.repositories.pending_order_confirmation import PendingOrderConfirmationRepository, PendingOrderConfirmationStatus
from src.exceptions.external_service_exception import ExternalServiceException
from enum import Enum
from src.clients.order_client import get_order_client
from src.exceptions.retryable import RetryableException
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)
_order_client = get_order_client()

class ReconciliationOutcome(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    UNREACHABLE = "unreachable"

def _next_state(attempts: int, outcome: ReconciliationOutcome, user_id: UUID) -> tuple[int, str, datetime | None]:
    new_attempts = attempts + 1
    if outcome == ReconciliationOutcome.NOT_FOUND:
        if new_attempts >= settings.reconciliation_max_attempts:
            logger.error(f"Reconciliation: order genuinely not found for user {user_id} after {new_attempts} checks — needs manual review")
            return new_attempts, PendingOrderConfirmationStatus.NEEDS_REVIEW, None
        return new_attempts, PendingOrderConfirmationStatus.PENDING, None
    if new_attempts >= settings.reconciliation_unreachable_alert_attempts:
        logger.critical(f"Reconciliation: order service unreachable for user {user_id} across {new_attempts} checks — investigate service availability")
    delay_seconds = min(
        settings.reconciliation_interval_seconds * (2 ** new_attempts),
        settings.reconciliation_unreachable_backoff_max_seconds,
    )
    next_check_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
    return new_attempts, PendingOrderConfirmationStatus.PENDING, next_check_at

async def _process_row(row_id: UUID) -> None:
    async with SessionFactory() as session:
        repo = PendingOrderConfirmationRepository(session)
        row = await repo.get_by_id(row_id)
        if row is None:
            return
        reference_id, attempts, user_id = row.reference_id, row.attempts, row.user_id
    try:
        existing_order = await _order_client.get_order_by_reference_id(reference_id)
        outcome = ReconciliationOutcome.FOUND if existing_order else ReconciliationOutcome.NOT_FOUND
    except RetryableException:
        outcome = ReconciliationOutcome.UNREACHABLE
    except ExternalServiceException:
        logger.exception(f"Reconciliation: unexpected service error checking user {user_id}")
        raise
    except Exception:
        logger.exception(f"Reconciliation: unexpected error checking user {user_id}")
        raise
    async with SessionFactory() as session:
        repo = PendingOrderConfirmationRepository(session)
        try:
            if outcome == ReconciliationOutcome.FOUND:
                updated = await repo.delete_if_in_progress(row_id)
            else:
                new_attempts, new_status, next_check_at = _next_state(attempts, outcome, user_id)
                updated = await repo.save_if_in_progress(row_id, new_status, new_attempts, next_check_at)
            if not updated:
                logger.warning(f"Reconciliation: row {row_id} was no longer IN_PROGRESS, skipping save")
            await session.commit()
        except Exception:
            logger.exception(f"Reconciliation: failed to persist result for row {row_id}")
            raise


async def _reconcile_once() -> None:
    async with SessionFactory() as session:
        repo = PendingOrderConfirmationRepository(session)
        claimed = await repo.claim_batch()
    semaphore = asyncio.Semaphore(settings.reconciliation_concurrency)

    async def _process_with_limit(row_id: UUID) -> None:
        async with semaphore:
            await _process_row(row_id)
    await asyncio.gather(*(_process_with_limit(row.id) for row in claimed))


async def run_reconciliation_worker() -> None:
    while True:
        try:
            await _reconcile_once()
        except Exception:
            logger.exception("Reconciliation worker iteration failed")
        await asyncio.sleep(settings.reconciliation_interval_seconds)