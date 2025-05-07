from fastapi.responses import Response
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from api.database import get_async_session

router = APIRouter(tags=['Memes'], prefix='/memes')


@router.post(
    '/generate',
    response_class=Response,
)
async def generate_meme(
    scream_id: int = Query(..., title='Scream ID'),
    session: AsyncSession = Depends(get_async_session),
):
    return Response(
        content=await service.generate_meme(session, scream_id),
        media_type='image/png',
    )
