"""`screams` routes."""

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas, service
from ..database import get_async_session

router = APIRouter(tags=['Screams'], prefix='/screams')


@router.get(
    '/',
    response_model=list[schemas.Scream],
)
async def get_screams(
    page: int = Query(..., title='Page'),
    limit: int = Query(..., title='Limit'),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get specified page of scream list.

    Args:
        page (int): Page number
        limit (int): Number of elements per page
        session (AsyncSession): Session
    """
    return await service.get_screams(session, page, limit)


@router.post(
    '/',
    response_model=schemas.Scream,
)
async def create_scream(
    scream: schemas.ScreamCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Create Scream.

    Args:
        scream (ScreamCreate): ScreamCreate schema
        session (AsyncSession): Session
    """
    return await service.create_scream(session, scream.user_id, scream.text)


@router.get(
    '/{scream_id}',
    response_model=schemas.Scream,
)
async def get_scream(
    scream_id: int = Path(..., title='Scream ID'),
    session: AsyncSession = Depends(get_async_session),
):
    """Get scream from scream ID."""
    return await service.get_scream(session, scream_id)


@router.delete('/{scream_id}')
async def delete_scream(
    scream_id: int = Path(..., title='Scream ID'),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete scream with specified ID."""
    await service.delete_scream(session, scream_id)


@router.post(
    '/{scream_id}/react',
    response_model=schemas.Scream,
)
async def react_on_scream(
    reaction: schemas.ReactionCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """React on scream."""
    return await service.react_on_scream(
        session,
        reaction.scream_id,
        reaction.user_id,
        reaction.reaction,
    )
