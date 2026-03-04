

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from db import get_session
from models import schemas
from services import AuthorService


router = APIRouter()

@router.post("/", response_model=schemas.AuthorRead)
async def create_author(author_in: schemas.AuthorCreate, session: AsyncSession = Depends(get_session)):
    author = await AuthorService.create_author(session, author_in)
    return author



@router.get("/{author_id}", response_model=schemas.AuthorRead)
async def read_author(author_id: int, session: AsyncSession = Depends(get_session)):
    author = await AuthorService.get_author_by_id(session, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author



@router.put("/{author_id}", response_model=schemas.AuthorRead)
async def update_author(author_id: int, author_in: schemas.AuthorUpdate, session: AsyncSession = Depends(get_session)):
    author = await AuthorService.update_author(session, author_id, author_in)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author



@router.delete("/{author_id}")
async def delete_author(author_id: int, session: AsyncSession = Depends(get_session)):
    success = await AuthorService.delete_author(session, author_id)
    if not success:
        raise HTTPException(status_code=404, detail="Author not found")
    return {"ok": True}
