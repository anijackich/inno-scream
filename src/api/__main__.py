import uvicorn
from fastapi import FastAPI

from api.config import settings
from api.screams import router as screams_router
from api.errors import register_exception_handler

app = FastAPI(**settings.app_meta.model_dump())

register_exception_handler(app)

app.include_router(screams_router)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        forwarded_allow_ips='*',
    )
