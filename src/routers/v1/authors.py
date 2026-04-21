from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import authors
from src.db import get_session
from src.services import AuthorService
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=authors.AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(author_in: authors.AuthorCreate, session: AsyncSession = Depends(get_session)):
    return await AuthorService(session).create_author(author_in)


@router.get("/{author_id}", response_model=authors.AuthorRead)
async def read_author(author_id: UUID, session: AsyncSession = Depends(get_session)):
    return await AuthorService(session).get_author_by_id(author_id)


@router.put("/{author_id}", response_model=authors.AuthorRead)
async def update_author(author_id: UUID, author_in: authors.AuthorUpdate, session: AsyncSession = Depends(get_session)):
    return await AuthorService(session).update_author(author_id, author_in)


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(author_id: UUID, session: AsyncSession = Depends(get_session)):
    await AuthorService(session).delete_author(author_id)