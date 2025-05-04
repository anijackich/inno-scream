from httpx import AsyncClient, Timeout
from pydantic import BaseModel, Field, ValidationError
from typing import List
from bs4 import BeautifulSoup
import json


class _MemeImage(BaseModel):
    name: str
    image_path: str


class _SearchQueryResponse(BaseModel):
    meme_templates: List[_MemeImage] = Field(alias='memeTemplates')


class Caption(BaseModel):
    """
    Rectangle representing a place for caption in meme.
    """
    x: int
    y: int
    width: int
    height: int


class _PageProps(BaseModel):
    initial_captions: List[Caption] = Field(alias='initialCaptions')


class MemeTemplate(BaseModel):
    """
    Image with caption rectangles.
    """
    image_url: str
    captions: List[Caption]


class Supermeme:
    """
    Wrapper class for Supermeme API.
    """

    def __init__(self, supermeme_url: str = 'https://supermeme.ai'):
        """
        Initialize a Supermeme instance.

        Args:
            supermeme_url (str): Base url of Supermeme.
        """
        self.client = AsyncClient(
            base_url=supermeme_url,
            timeout=Timeout(30.0),
        )

    async def _search_memes(self, query: str) -> List[_MemeImage]:
        response = await self.client.get(
            '/api/search',
            params={'searchQuery': query},
        )
        response.raise_for_status()

        try:
            response = _SearchQueryResponse.model_validate(response.json())
        except ValidationError:
            raise ValueError('No meme templates found (invalid json response)')

        if len(response.meme_templates) == 0:
            raise ValueError(f'No meme templates found for query "{query}"')

        return response.meme_templates

    async def _get_meme_captions(self, meme: _MemeImage) -> List[Caption]:
        page = await self.client.get(f'/meme/{meme.name}')
        page.raise_for_status()

        soup = BeautifulSoup(page.content, 'html.parser')
        next_data = soup.find(id='__NEXT_DATA__')

        if next_data is None:
            raise ValueError('No captions found (__NEXT_DATA__ is absent)')

        next_data = json.loads(next_data.text)

        if 'props' not in next_data:
            raise ValueError('No captions found (props is absent)')

        if 'pageProps' not in next_data['props']:
            raise ValueError('No captions found (pageProps is absent)')

        try:
            page_props = _PageProps.model_validate(
                next_data['props']['pageProps']
            )
        except ValidationError:
            raise ValueError('No captions found (invalid json response)')

        return page_props.initial_captions

    async def get_meme_template(self, query: str) -> MemeTemplate:
        """
        Finds the most suitable template for given meme text.

        Args:
            query (str): Meme query.

        Returns:
            MemeTemplate: Image with caption rectangles.

        Raises:
            httpx.HTTPStatusError
            httpx.RequestError
            httpx.TimeoutException
            httpx.NetworkError
            ValueError
        """
        memes = await self._search_memes(query)
        captions = await self._get_meme_captions(memes[0])

        return MemeTemplate(
            image_url=memes[0].image_path,
            captions=captions,
        )
