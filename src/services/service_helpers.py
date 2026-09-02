import logging
from uuid import UUID

from src.exceptions.not_found import NotFoundException
from src.repositories.base_repository import BaseRepository, ModelType

logger = logging.getLogger(__name__)


async def get_by_id_or_fail(repo: BaseRepository[ModelType], obj_id: UUID, entity_name: str, extra: dict | None = None) -> ModelType:
    entity = await repo.get_by_id(obj_id)
    if not entity:
        logger.error(f"Entity '{entity_name}' with id {obj_id} not found", extra=extra)
        raise NotFoundException(f"{entity_name} not found")
    return entity