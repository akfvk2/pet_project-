from src.repositories.BaseRepository import BaseRepository
from src.models.profile import ProfileModel
from sqlalchemy.ext.asyncio import AsyncSession

class ProfileRepository(BaseRepository[ProfileModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProfileModel, session)