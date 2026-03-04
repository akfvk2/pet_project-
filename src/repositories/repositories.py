from requests import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import users, schemas

#User
class UserRepository:
    @staticmethod
    async def create(session: AsyncSession, user_in: schemas.UserCreate):
        user = users.UserModel(username=user_in.username)
        if hasattr(user_in, "profile") and user_in.profile:
            profile = users.ProfileModel(bio=user_in.profile.bio)
            user.profile = profile
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int):
        result = await session.execute(select(users.UserModel).where(users.UserModel.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, user_id: int, user_in: schemas.UserUpdate):
        result = await session.execute(select(users.UserModel).where(users.UserModel.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        user.username = user_in.username
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete(session: AsyncSession, user_id: int):
        result = await session.execute(select(users.UserModel).where(users.UserModel.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False
        await session.delete(user)
        await session.commit()
        return True

#Profile

class ProfileRepository:
    @staticmethod
    async def create(session: AsyncSession, profile_in: schemas.ProfileBase):
        profile = users.ProfileModel(bio=profile_in.bio, user_id=profile_in.user_id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def get_by_id(session: AsyncSession, profile_id: int):
        result = await session.execute(select(users.ProfileModel).where(users.ProfileModel.id == profile_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, profile_id: int, profile_in: schemas.ProfileBase):
        result = await session.execute(select(users.ProfileModel).where(users.ProfileModel.id == profile_id))
        profile = result.scalar_one_or_none()
        if not profile:
            return None
        profile.bio = profile_in.bio
        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def delete(session: AsyncSession, profile_id: int):
        result = await session.execute(select(users.ProfileModel).where(users.ProfileModel.id == profile_id))
        profile = result.scalar_one_or_none()
        if not profile:
            return False
        await session.delete(profile)
        await session.commit()
        return True


class AuthorRepository:
    @staticmethod
    async def create(session: AsyncSession, author_in: schemas.AuthorCreate):
        author = users.Author(name=author_in.name)
        session.add(author)
        await session.commit()
        await session.refresh(author)
        return author

    @staticmethod
    async def get_by_id(session: AsyncSession, author_id: int):
        result = await session.execute(select(users.Author).where(users.Author.id == author_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, author_id: int, author_in: schemas.AuthorUpdate):
        result = await session.execute(select(users.Author).where(users.Author.id == author_id))
        author = result.scalar_one_or_none()
        if not author:
            return None
        author.name = author_in.name
        await session.commit()
        await session.refresh(author)
        return author

    @staticmethod
    async def delete(session: AsyncSession, author_id: int):
        result = await session.execute(select(users.Author).where(users.Author.id == author_id))
        author = result.scalar_one_or_none()
        if not author:
            return False
        await session.delete(author)
        await session.commit()
        return True


class BookRepository:
    @staticmethod
    async def create(session: AsyncSession, book_in: schemas.BookBase):
        book = users.Book(title=book_in.title, author_id=book_in.author_id)
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

    @staticmethod
    async def get_by_id(session: AsyncSession, book_id: int):
        result = await session.execute(select(users.Book).where(users.Book.id == book_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, book_id: int, book_in: schemas.BookBase):
        result = await session.execute(select(users.Book).where(users.Book.id == book_id))
        book = result.scalar_one_or_none()
        if not book:
            return None
        book.title = book_in.title
        book.author_id = book_in.author_id
        await session.commit()
        await session.refresh(book)
        return book

    @staticmethod
    async def delete(session: AsyncSession, book_id: int):
        result = await session.execute(select(users.Book).where(users.Book.id == book_id))
        book = result.scalar_one_or_none()
        if not book:
            return False
        await session.delete(book)
        await session.commit()
        return True


class StudentRepository:
    @staticmethod
    async def create(session: AsyncSession, student_in: schemas.StudentCreate):
        student = users.Students(name=student_in.name)
        if student_in.courses:
            result = await session.execute(select(users.Course).where(users.Course.id.in_(student_in.courses)))
            courses = result.scalars().all()
            student.courses = list(courses)
        session.add(student)
        await session.commit()
        await session.refresh(student)
        return student

    @staticmethod
    async def get_by_id(session: AsyncSession, student_id: int):
        result = await session.execute(select(users.Students).where(users.Students.id == student_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, student_id: int, student_in: schemas.StudentUpdate):
        result = await session.execute(select(users.Students).where(users.Students.id == student_id))
        student = result.scalar_one_or_none()
        if not student:
            return None
        student.name = student_in.name
        if student_in.courses is not None:
            result = await session.execute(select(users.Course).where(users.Course.id.in_(student_in.courses)))
            courses = result.scalars().all()
            student.courses = list(courses)
        await session.commit()
        await session.refresh(student)
        return student

    @staticmethod
    async def delete(session: AsyncSession, student_id: int):
        result = await session.execute(select(users.Students).where(users.Students.id == student_id))
        student = result.scalar_one_or_none()
        if not student:
            return False
        await session.delete(student)
        await session.commit()
        return True



class CourseRepository:
    @staticmethod
    async def create(session: AsyncSession, course_in: schemas.CourseBase):
        course = users.Course(title=course_in.title)
        session.add(course)
        await session.commit()
        await session.refresh(course)
        return course

    @staticmethod
    async def get_by_id(session: AsyncSession, course_id: int):
        result = await session.execute(select(users.Course).where(users.Course.id == course_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(session: AsyncSession, course_id: int, course_in: schemas.CourseBase):
        result = await session.execute(select(users.Course).where(users.Course.id == course_id))
        course = result.scalar_one_or_none()
        if not course:
            return None
        course.title = course_in.title
        await session.commit()
        await session.refresh(course)
        return course

    @staticmethod
    async def delete(session: AsyncSession, course_id: int):
        result = await session.execute(select(users.Course).where(users.Course.id == course_id))
        course = result.scalar_one_or_none()
        if not course:
            return False
        await session.delete(course)
        await session.commit()
        return True