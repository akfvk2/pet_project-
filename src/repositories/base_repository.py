from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from  typing import TypeVar, Generic, Type
from src.models.base_model import Base
from uuid import UUID

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model:Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        return obj

    async def get_by_id(self, obj_id: UUID) -> ModelType | None:
        entity = await self.session.get(self.model, obj_id)
        return entity

    async def update(self, obj: ModelType) -> ModelType:
        return obj

    async def delete(self, obj: ModelType) -> bool:
        obj.is_deleted = True
        return True
