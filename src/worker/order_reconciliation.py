import asyncio
import logging

from src.db import SessionFactory
from src.config import settings
from src.repositories.pending_order_confirmation import PendingOrderConfirmationRepository
from src.repositories.user import UserRepository
from src.clients.order_client import OrderServiceClient
from src.exceptions.order_service_error import ServiceException

logger = logging.getLogger(__name__)



async def _reconcile_once() -> None:
    async with SessionFactory() as session:
        pending_repo = PendingOrderConfirmationRepository(session)
        users_repo = UserRepository(session)
        order_client = OrderServiceClient()

        for row in await pending_repo.get_all_pending():
            try:
                existing_orders = await order_client.get_orders_by_user_id(row.user_id)
            except ServiceException:
                logger.warning(f"Reconciliation: order service still unreachable for user {row.user_id}")
                continue  # попробуем в следующий цикл, попытки не трогаем

            if existing_orders:
                await pending_repo.delete(row)
                continue

            row.attempts += 1
            if row.attempts >= settings.reconciliation_max_attempts:
                user = await users_repo.get_by_id(row.user_id)
                if user:
                    await users_repo.delete(user)
                    logger.warning(f"Reconciliation: compensated user {row.user_id} after {row.attempts} failed checks")
                await pending_repo.delete(row)

        await session.commit()

async def run_reconciliation_worker() -> None:
    while True:
        try:
            await _reconcile_once()
        except Exception:
            logger.exception("Reconciliation worker iteration failed")
        await asyncio.sleep(settings.reconciliation_interval_seconds)