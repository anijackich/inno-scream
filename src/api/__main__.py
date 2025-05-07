import uvicorn
from fastapi import FastAPI

from api.config import settings
from api.database import create_database
from api.errors import register_exception_handler

from api.memes import router as memes_router
from api.screams import router as screams_router
from api.analytics import router as analytics_router


async def startup() -> None:
    await create_database()


app = FastAPI(
    **settings.app_meta.model_dump(),
    on_startup=[startup]
)

register_exception_handler(app)

app.include_router(screams_router)
app.include_router(analytics_router)
app.include_router(memes_router)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        forwarded_allow_ips='*',
    )
