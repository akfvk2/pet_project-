from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schemas import authors
from src.db import get_session
from src.services import AuthorService


router = APIRouter()

@router.post("/", response_model=authors.AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(author_in: authors.AuthorCreate, session: AsyncSession = Depends(get_session)):
    return await AuthorService.create_author(session, author_in)



@router.get("/{author_id}", response_model=authors.AuthorRead)
async def read_author(author_id: int, session: AsyncSession = Depends(get_session)):
    return await AuthorService.get_author_by_id(session, author_id)



@router.put("/{author_id}", response_model=authors.AuthorRead)
async def update_author(author_id: int, author_in: authors.AuthorUpdate, session: AsyncSession = Depends(get_session)):
    return await AuthorService.update_author(session, author_id, author_in)



@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(author_id: int, session: AsyncSession = Depends(get_session)):
    await AuthorService.delete_author(session, author_id)