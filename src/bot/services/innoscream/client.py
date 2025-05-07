from typing import Literal
from httpx import AsyncClient

from .models import Scream, Stats


class InnoScreamAPI:
    def __init__(self, base_url: str):
        self.client = AsyncClient(base_url=base_url, follow_redirects=True)

    async def create_scream(self, user_id: int, text: str) -> Scream:
        res = await self.client.post(
            '/screams',
            json={
                'user_id': user_id,
                'text': text,
            }
        )
        res.raise_for_status()

        return Scream.model_validate(res.json())

    async def get_scream(self, scream_id: int) -> Scream:
        res = await self.client.get(f'/screams/{scream_id}')
        res.raise_for_status()

        return Scream.model_validate(res.json())

    async def delete_scream(self, scream_id: int) -> None:
        res = await self.client.delete(f'/screams/{scream_id}')
        res.raise_for_status()

    async def react_on_scream(
        self,
        scream_id: int,
        user_id: int,
        reaction: str,
    ) -> Scream:
        res = await self.client.post(
            f'/screams/{scream_id}/react',
            json={
                'scream_id': scream_id,
                'user_id': user_id,
                'reaction': reaction,
            }
        )
        res.raise_for_status()

        return Scream.model_validate(res.json())

    async def get_stats(self, user_id: int) -> Stats:
        res = await self.client.get(f'/analytics/{user_id}/stats')
        res.raise_for_status()

        return Stats.model_validate(res.json())

    async def get_graph(
        self,
        user_id: int,
        period: Literal['week', 'month', 'year']
    ) -> bytes:
        res = await self.client.get(
            f'/analytics/{user_id}/graph',
            params={'period': period}
        )
        res.raise_for_status()

        return res.content

    async def get_most_voted_scream(
        self,
        period: Literal['day', 'week', 'month', 'year']
    ) -> Scream | None:
        res = await self.client.get(
            '/analytics/getMostVoted',
            params={'period': period}
        )
        res.raise_for_status()

        return Scream.model_validate(res.json()) if res.content else None

    async def generate_meme(self, scream_id: int) -> bytes:
        res = await self.client.post(
            '/memes/generate',
            params={'scream_id': scream_id},
            timeout=60
        )
        res.raise_for_status()

        return res.content
