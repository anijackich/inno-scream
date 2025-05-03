from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from api import models
from .exceptions import ScreamNotFound


def get_scream_reactions(scream: models.Scream) -> dict[str: int]:
    reactions = defaultdict(int)
    for reaction in scream.reactions:
        reactions[reaction.reaction] += 1

    return dict(reactions)


def scream_orm2schema(scream: models.Scream) -> schemas.Scream:
    return schemas.Scream(
        scream_id=scream.id,
        user_id=scream.user_id,
        text=scream.text,
        created_at=scream.created_at,
        reactions=get_scream_reactions(scream),
    )


async def create_scream(
        session: AsyncSession,
        user_id: int,
        text: str,
) -> schemas.Scream:
    scream = models.Scream(user_id=user_id, text=text)
    session.add(scream)

    await session.commit()
    await session.refresh(scream)

    return scream_orm2schema(scream)


async def get_scream(
        session: AsyncSession,
        scream_id: int
) -> schemas.Scream:
    scream = await session.get(models.Scream, scream_id)
    if not scream:
        raise ScreamNotFound()

    return scream_orm2schema(scream)


async def get_screams(
        session: AsyncSession,
        page: int,
        limit: int,
) -> list[schemas.Scream]:
    screams = (await session.execute(
        select(models.Scream)
        .order_by(models.Scream.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )).scalars().all()

    return list(map(scream_orm2schema, screams))


async def delete_scream(
        session: AsyncSession,
        scream_id: int,
) -> None:
    scream = await session.get(models.Scream, scream_id)
    if not scream:
        raise ScreamNotFound()

    await session.delete(scream)
    await session.commit()


async def react_on_scream(
        session: AsyncSession,
        scream_id: int,
        user_id: int,
        reaction: str,
) -> schemas.Scream:
    scream = await session.get(models.Scream, scream_id)
    if not scream:
        raise ScreamNotFound()

    user_reaction = next(
        (r for r in scream.reactions if r.user_id == user_id),
        None,
    )

    if user_reaction:
        await session.delete(user_reaction)

    if not user_reaction or user_reaction.reaction != reaction:
        reaction = models.Reaction(
            user_id=user_id,
            scream_id=scream_id,
            reaction=reaction,
        )
        session.add(reaction)

    await session.commit()
    await session.refresh(scream)

    return scream_orm2schema(scream)
