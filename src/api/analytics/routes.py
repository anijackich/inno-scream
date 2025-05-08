"""`analytics` routes."""

from typing import Literal

from fastapi.responses import Response
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas, service
from api.screams import Scream
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
    """Get statistics for user."""
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
    """Get statistics graph for user and time period."""
    return Response(
        content=await service.get_graph(session, user_id, period),
        media_type='image/png',
    )


@router.get('/getMostVoted', response_model=Scream | None)
async def get_most_voted(
    period: Literal['day', 'week', 'month', 'year'] = Query(
        ..., title='Period'
    ),
    session: AsyncSession = Depends(get_async_session),
):
    """Get most voted scream in time period."""
    return await service.get_most_voted(session, period)
