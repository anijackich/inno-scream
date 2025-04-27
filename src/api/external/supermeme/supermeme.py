from httpx import AsyncClient, Timeout
from pydantic import BaseModel, Field
from typing import List
from bs4 import BeautifulSoup
import json


class _MemeImage(BaseModel):
    name: str
    image_path: str


class _SearchQueryResponse(BaseModel):
    meme_templates: List[_MemeImage] = Field(alias="memeTemplates")


class Caption(BaseModel):
    """
    Rectange representing a place for caption in meme.
    """
    x: int
    y: int
    width: int
    height: int


class _PageProps(BaseModel):
    initial_captions: List[Caption] = Field(alias="initialCaptions")


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

    def __init__(self, supermeme_url: str = "https://supermeme.ai"):
        """
        Initialize a Supermeme instance.

        Args:
            supermeme_url (str): Base url of Supermeme.
        """
        self.client = AsyncClient(base_url=supermeme_url,
                                  timeout=Timeout(30.0))

    async def get_template_for_text(self, text: str) -> MemeTemplate:
        """
        Finds the most suitable template for given meme text.

        Args:
            text (str): Meme text.

        Returns:
            MemeTemplate: Image with caption rectangles.
        """
        response = await self.client.get("/api/search",
                                         params={"searchQuery": text})
        response.raise_for_status()

        response = _SearchQueryResponse.model_validate(response.json())
        if len(response.meme_templates) == 0:
            raise ValueError(f'No meme templates found for query "{text}"')
        image = response.meme_templates[0]

        page = await self.client.get(f"/meme/{image.name}")
        page.raise_for_status()
        html = page.text

        soup = BeautifulSoup(html, "html.parser")
        next_data = soup.find(id="__NEXT_DATA__")

        if next_data is None:
            raise ValueError("No captions found (__NEXT_DATA__ is absent)")

        next_data_json = json.loads(next_data.text)

        page_props = _PageProps.model_validate(
            next_data_json["props"]["pageProps"])

        return MemeTemplate(image_url=image.image_path,
                            captions=page_props.initial_captions)
