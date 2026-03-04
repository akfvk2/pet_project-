import uvicorn
import asyncio

import routers.users, routers.students, routers.authors
from fastapi import FastAPI
from db import engine
from models.users import Base

async def main() -> None:
    uvicorn.run('application:get_app', host='localhost', port=8000, reload=True, factory=True)

if __name__ == '__main__':
    asyncio.run(main())
app = FastAPI

@app.on_event("startup")
async def on_startup() -> None:
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

app.include_router(routers.users.router, prefix="/users", tags=["users"])
app.include_router(routers.authors.router, prefix="/authors", tags=["authors"])
app.include_router(routers.students.router, prefix="/students", tags=["students"])