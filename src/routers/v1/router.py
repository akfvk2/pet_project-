from fastapi import APIRouter
from src.routers.v1 import users, authors, students

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
api_v1_router.include_router(authors.router, prefix="/authors", tags=["authors"])
api_v1_router.include_router(students.router, prefixб ="/students", tags=["students"])