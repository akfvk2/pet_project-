import uvicorn
import asyncio

from healthcheck.router import router


async def main() -> None:
    uvicorn.run('application:get_app', host='localhost', port=8000, reload=True, factory=True)

if __name__ == '__main__':
    asyncio.run(main())


app.include_router(router.router, prefix="/users", tags=["users"])