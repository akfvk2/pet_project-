from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.testing.pickleable import User

from src.models import users
from  typing import TypeVar, Generic, Type
from src.models.users import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model:Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session


    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, obj_id: int) -> ModelType | None:
        result = await self.session.execute(select(self.model).where(getattr(self.model.id == obj_id)))
        return result.scalar_one_or_none()

    async def update(self, obj: ModelType) -> ModelType:
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> bool:
        await self.session.delete(obj)
        await self.session.flush()
        return True



class UserRepository(BaseRepository[users.UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(users.UserModel, session)

class ProfileRepository(BaseRepository[users.ProfileModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(users.ProfileModel, session)

class AuthorRepository(BaseRepository[users.Author]):
    def __init__(self, session: AsyncSession):
        super().__init__(users.Author, session)

class BookRepository(BaseRepository[users.Book]):
    def __init__(self, session: AsyncSession):
        super().__init__(users.Book, session)

class StudentRepository(BaseRepository[users.Students]):
    def __init__(self, session: AsyncSession):
        super().__init__(users.Students, session)

class CourseRepository(BaseRepository[users.Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(users.Course, session)
