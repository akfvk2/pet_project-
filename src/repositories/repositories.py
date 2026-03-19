from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import users


#User
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: users.UserModel ):
        self.session.add(user)
        await self.session.refresh(user)
        return user


    async def get_by_id(self, user_id: int):
        result = await self.session.execute(select(users.UserModel).where(users.UserModel.id == user_id))
        return result.scalar_one_or_none()


    async def update(self, user: users.UserModel ):
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user


    async def delete(self, user: users.UserModel):
        await self.session.delete(user)
        await self.session.flush()
        return True

#Profile

class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, profile: users.ProfileModel):
        self.session.add(profile)
        await self.session.refresh(profile)
        return profile


    async def get_by_id(self, profile_id: int):
        result = await self.session.execute(select(users.ProfileModel).where(users.ProfileModel.id == profile_id))
        return result.scalar_one_or_none()


    async def update(self,  profile: users.ProfileModel):
        self.session.add(profile)
        await self.session.refresh(profile)
        return profile


    async def delete(self, profile: users.ProfileModel):
        await self.session.delete(profile)
        await self.session.flush()
        return True


class AuthorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, author: users.Author ):
        self.session.add(author)
        await self.session.flush()
        await self.session.refresh(author)
        return author


    async def get_by_id(self, author_id: int ):
        result = await self.session.execute(select(users.Author).where(users.Author.id == author_id))
        return result.scalar_one_or_none()


    async def update(self, author: users.Author ):
        self.session.add(author)
        await self.session.flush()
        await self.session.refresh(author)
        return author


    async def delete(self, author: users.Author ):
        await self.session.delete(author)
        await self.session.flush()
        return True


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, book: users.Book):
        self.session.add(book)
        await self.session.flush()
        await self.session.refresh(book)
        return book


    async def get_by_id(self, book_id: int):
        result = await self.session.execute(select(users.Book).where(users.Book.id == book_id))
        return result.scalar_one_or_none()


    async def update(self, book: users.Book):
        self.session.add(book)
        await self.session.flush()
        await self.session.refresh(book)
        return book


    async def delete(self, book: users.Book):
        await self.session.delete(book)
        await self.session.flush()
        return True


class StudentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, student: users.Students):
        self.session.add(student)
        await self.session.flush()
        await self.session.refresh(student)
        return student


    async def get_by_id(self, student_id: int):
        result = await self.session.execute(select(users.Students).where(users.Students.id == student_id))
        return result.scalar_one_or_none()


    async def update(self, student: users.Students):
        self.session.add(student)
        await self.session.flush()
        await self.session.refresh(student)
        return student


    async def delete(self, student: users.Students):
        await self.session.delete(student)
        await self.session.flush()
        return True



class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, course: users.Course):
        self.session.add(course)
        await self.session.flush()
        await self.session.refresh(course)
        return course


    async def get_by_id(self, course_id: int):
        result = await self.session.execute(select(users.Course).where(users.Course.id == course_id))
        return result.scalar_one_or_none()


    async def update(self, course: users.Course):
        self.session.add(course)
        await self.session.flush()
        await self.session.refresh(course)
        return course


    async def delete(self, course: users.Course):
        await self.session.delete(course)
        await self.session.flush()
        return True