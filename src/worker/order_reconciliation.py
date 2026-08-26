import asyncio
import logging
from uuid import UUID
from src.db import SessionFactory
from src.config import settings
from src.repositories.pending_confirmation import PendingConfirmationRepository, PendingConfirmationStatus
from src.exceptions.external_service_exception import ExternalServiceException
from enum import Enum
from src.clients.order_client import get_order_client
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)
_order_client = get_order_client()

class ReconciliationOutcome(str, Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    UNREACHABLE = "unreachable"

def _next_state(not_found_attempts: int, unreachable_attempts: int, outcome: ReconciliationOutcome, user_id: UUID) -> tuple[int, int, str, datetime | None]:
    if outcome == ReconciliationOutcome.NOT_FOUND:
        new_not_found_attempts = not_found_attempts + 1
        if new_not_found_attempts >= settings.reconciliation_max_attempts:
            logger.error(f"Reconciliation: order genuinely not found for user {user_id} after {new_not_found_attempts} checks — needs manual review")
            return new_not_found_attempts, unreachable_attempts, PendingConfirmationStatus.NEEDS_REVIEW, None
        return new_not_found_attempts, unreachable_attempts, PendingConfirmationStatus.PENDING, None
    new_unreachable_attempts = unreachable_attempts + 1
    if new_unreachable_attempts >= settings.reconciliation_unreachable_alert_attempts:
        logger.critical(
            f"Reconciliation: order service unreachable for user {user_id} across {new_unreachable_attempts} checks — investigate service availability")
    delay_seconds = min(
        settings.reconciliation_interval_seconds * (2 ** new_unreachable_attempts),
        settings.reconciliation_unreachable_backoff_max_seconds,
    )
    next_check_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
    return not_found_attempts, new_unreachable_attempts, PendingConfirmationStatus.PENDING, next_check_at

async def _process_row(row_id: UUID) -> None:
    async with SessionFactory() as session:
        repo = PendingConfirmationRepository(session)
        row = await repo.get_by_id(row_id)
        if row is None:
            return
        reference_id = row.reference_id
        not_found_attempts, unreachable_attempts, user_id, version = row.not_found_attempts, row.unreachable_attempts, row.user_id, row.version
    try:
        existing_orders = await asyncio.wait_for(
            _order_client.get_orders_by_user_id(user_id),
            timeout=settings.reconciliation_row_processing_timeout_seconds,
        )
        existing_order = next((o for o in existing_orders if o.reference_id == reference_id), None)
        outcome = ReconciliationOutcome.FOUND if existing_order else ReconciliationOutcome.NOT_FOUND
    except asyncio.TimeoutError:
        outcome = ReconciliationOutcome.UNREACHABLE
    except ExternalServiceException:
        outcome = ReconciliationOutcome.UNREACHABLE
    except Exception:
        logger.exception(f"Reconciliation: unexpected error checking user {user_id}")
        raise
    async with SessionFactory() as session:
        repo = PendingConfirmationRepository(session)
        try:
            if outcome == ReconciliationOutcome.FOUND:
                updated = await repo.delete_if_in_progress(row_id, version)
            else:
                new_not_found, new_unreachable, new_status, next_check_at = _next_state(
                    not_found_attempts, unreachable_attempts, outcome, user_id
                )
                updated = await repo.save_if_in_progress(row_id, new_status, new_not_found, new_unreachable, next_check_at, version)
            if not updated:
                logger.warning(f"Reconciliation: row {row_id} was no longer at expected version, skipping save")
            await session.commit()
        except Exception:
            logger.exception(f"Reconciliation: failed to persist result for row {row_id}")
            raise


async def _reconcile_once() -> None:
    async with SessionFactory() as session:
        repo = PendingConfirmationRepository(session)
        claimed = await repo.claim_batch()
        await session.commit()
    chunk_size = settings.reconciliation_concurrency
    for i in range(0, len(claimed), chunk_size):
        chunk = claimed[i:i + chunk_size]
        results = await asyncio.gather(
            *(_process_row(row.id) for row in chunk),
            return_exceptions=True,)
        for row, result in zip(chunk, results):
            if isinstance(result, Exception):
                logger.exception(f"Reconciliation: failed to process row {row.id}", exc_info=result)




async def run_reconciliation_worker() -> None:
    while True:
        try:
            await _reconcile_once()
        except Exception:
            logger.exception("Reconciliation worker iteration failed")
        await asyncio.sleep(settings.reconciliation_interval_seconds)