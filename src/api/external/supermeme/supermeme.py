import json
from typing import List

from bs4 import BeautifulSoup
from httpx import AsyncClient, Timeout
from pydantic import BaseModel, Field, ValidationError


class Caption(BaseModel):
    """
    Rectangle representing a place for caption in meme.
    """
    x: int
    y: int
    text: str
    width: int
    height: int
    language: str
    font_size: int = Field(alias='fontSize')
    font_family: str | None = Field(alias='fontFamily')
    rotate_angle: int = Field(alias='rotateAngle')


class MemeTemplate(BaseModel):
    name: str
    image_path: str
    description: str
    meme_text: str


class MemeTemplateProps(BaseModel):
    page_title: str = Field(alias='pageTitle')
    image_src: str = Field(alias='imageSrc')
    image_name: str = Field(alias='imageName')
    image_description: str = Field(alias='imageDescription')
    image_width: int = Field(alias='imageWidth')
    image_height: int = Field(alias='imageHeight')
    initial_captions: List[Caption] = Field(alias='initialCaptions')


class _PageProps(BaseModel):
    image_width: int = Field(alias='imageWidth')
    image_height: int = Field(alias='imageHeight')
    initial_captions: List[Caption] = Field(alias='initialCaptions')


class Supermeme:
    """
    Wrapper class for Supermeme API.
    """

    def __init__(self, base_url: str = 'https://supermeme.ai', timeout: float = 30.0):
        """
        Initialize a Supermeme instance.

        Args:
            base_url (str): Base url of Supermeme.
            timeout (float): Timeout for requests to Supermeme.
        """
        self.client = AsyncClient(
            base_url=base_url,
            timeout=Timeout(timeout),
        )

    async def search_meme_templates(self, query: str) -> List[MemeTemplate]:
        response = await self.client.get(
            '/api/search',
            params={'searchQuery': query},
        )
        response.raise_for_status()

        try:
            meme_templates = [
                MemeTemplate.model_validate(template)
                for template in response.json()['memeTemplates']
            ]
        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            raise ValueError('Invalid json response') from e

        return meme_templates

    async def get_meme_template_props(self, meme: MemeTemplate) -> MemeTemplateProps:
        response = await self.client.get(f'/meme/{meme.name}')
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        next_data = soup.find(id='__NEXT_DATA__')

        if next_data is None:
            raise ValueError('No data found (__NEXT_DATA__ is absent)')

        next_data = json.loads(next_data.text)

        try:
            print(next_data['props']['pageProps'])
            meme_template_props = MemeTemplateProps.model_validate(
                next_data['props']['pageProps']
            )
        except (KeyError, ValidationError) as e:
            raise ValueError('Invalid __NEXT_DATA__ schema') from e

        return meme_template_props
