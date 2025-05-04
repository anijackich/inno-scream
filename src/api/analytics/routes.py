from typing import Literal

from fastapi.responses import Response
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas, service
from api.database import get_async_session

router = APIRouter(tags=['Analytics'], prefix='/analytics')


@router.get(
    '/{user_id}/stats',
    response_model=schemas.Stats,
)
async def get_stats(
        user_id: int = Path(..., title='User ID'),
        session: AsyncSession = Depends(get_async_session),
):
    return await service.get_stats(session, user_id)


@router.get(
    '/{user_id}/graph',
    response_class=Response,
)
async def get_graph(
        user_id: int = Path(..., title='User ID'),
        period: Literal['week', 'month', 'year'] = Query(..., title='Period'),
        session: AsyncSession = Depends(get_async_session),
):
    return Response(
        content=await service.get_graph(session, user_id, period),
        media_type='image/png'
    )
