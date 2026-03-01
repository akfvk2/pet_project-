from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_session
from ..models import schemas, users



router = APIRouter()



@router.get('/healthcheck')
async def healthcheck() -> Dict[str, str]:
    return {'status': 'ok'}

#user

@router.post("/", response_model=schemas.UserRead)
async def create_user(user_in: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    user = users.UserModel(bio=user_in.profilmodel.bio)

    if user_in.profile:
        profile = users.ProfileModel(bio=user_in.profile.bio)
        user.profile = profile

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user



@router.get("/{user_id}", response_model=schemas.UserRead)
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(users.UserModel).where(users.UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schemas.UserRead)
async def update_user(user_id: int, user_in: schemas.UserUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(users.UserModel).where(users.UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = user_in.username

    if user_in.profile is not None:
        if user.profile is None:
            user.profile = users.ProfileModel(bio=user_in.profile.bio)
        else:
            user.profile.bio = user_in.profile.bio

    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(users.UserModel).where(users.UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(user)
    await session.commit()
    return {"ok": True}

#students

@router.post("/", response_model=schemas.StudentRead)
async def create_student(student_in: schemas.StudentCreate, session: AsyncSession = Depends(get_session)):
    student = users.Students(name=student_in.name)

    if student_in.courses:
        result = await session.execute(select(users.Course).where(users.Course.id.in_(student_in.courses)))
        courses = result.scalars().all()
        student.courses = list(courses)

    session.add(student)
    await session.commit()
    await session.refresh(student)
    return student


@router.get("/{student_id}", response_model=schemas.StudentRead)
async def read_student(student_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(users.Students).where(users.Students.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=schemas.StudentRead)
async def update_student(student_id: int, student_in: schemas.StudentUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(users.Students).where(users.Students.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = student_in.name

    if student_in.courses is not None:
        result = await session.execute(select(users.Course).where(users.Course.id.in_(student_in.courses)))
        courses = result.scalars().all()
        student.courses = list(courses)

    await session.commit()
    await session.refresh(student)
    return student


@router.delete("/{student_id}")
async def delete_student(student_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(users.Students).where(users.Students.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    await session.delete(student)
    await session.commit()
    return {"ok": True}


#author

@router.post("/", response_model=schemas.AuthorRead)
async def create_author(author_in: schemas.AuthorCreate, session: AsyncSession = Depends(get_session)):
    author = users.Author(name=author_in.name)

    if author_in.books:
        for book_data in author_in.books:
            book = users.Book(title=book_data.title)
            author.books.append(book)

    session.add(author)
    await session.commit()
    await session.refresh(author)
    return author


@router.get("/{author_id}", response_model=schemas.AuthorRead)
async def read_author(author_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(users.Author).where(users.Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@router.put("/{author_id}", response_model=schemas.AuthorRead)
async def update_author(author_id: int, author_in: schemas.AuthorUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(users.Author).where(users.Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    author.name = author_in.name

    if author_in.books is not None:
        author.books.clear()
        for book_data in author_in.books:
            book = users.Book(title=book_data.title)
            author.books.append(book)

    await session.commit()
    await session.refresh(author)
    return author


@router.delete("/{author_id}")
async def delete_author(author_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(users.Author).where(users.Author.id == author_id))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    await session.delete(author)
    await session.commit()
    return {"ok": True}
