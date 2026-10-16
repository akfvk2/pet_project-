from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.repositories.base_repository import BaseRepository
from src.models.room import RoomModel
from sqlalchemy.ext.asyncio import AsyncSession

class RoomRepository(BaseRepository[RoomModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(RoomModel, session)

    async def get_by_id(self, obj_id: UUID) -> RoomModel | None:
        stmt = (
            select(RoomModel)
            .where(RoomModel.id == obj_id)
            .options(selectinload(RoomModel.reservation))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()