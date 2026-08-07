from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import APIRouter
from src.routers.v1 import users, authors, students
from src.exceptions.base import AppException, app_exception_handler
import asyncio
import contextlib
from src.worker.order_reconciliation import run_reconciliation_worker
from src.clients.order_client import get_order_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_reconciliation_worker())
    yield
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task
    await get_order_client().close()


def get_app() -> FastAPI:
    app = FastAPI(
        docs_url='/docs',
        openapi_url='/openapi.json',
        default_response_class=UJSONResponse,
        lifespan=lifespan,
    )

    app.add_exception_handler(AppException, app_exception_handler)


    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    api_v1_router = APIRouter(prefix="/v1")

    api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
    api_v1_router.include_router(authors.router, prefix="/authors", tags=["authors"])
    api_v1_router.include_router(students.router, prefix="/students", tags=["students"])

    app.include_router(api_v1_router)
    return app