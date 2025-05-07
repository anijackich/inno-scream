from io import BytesIO

import httpx
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import settings
from api.screams import get_scream
from api.external.supermeme import Supermeme, MemeTemplateProps


def get_text_sizes(text: str, font: ImageFont) -> tuple[float, float]:
    left, top, right, bottom = font.getbbox(text)
    return right - left, bottom - top


def split_text_to_lines(
        width: float,
        text: str,
        font: ImageFont,
) -> list[str]:
    break_width = get_text_sizes(' ', font)[0]

    lines = []
    current_line = []
    current_width = 0

    for word in text.split():
        word_width = get_text_sizes(word, font)[0]
        if current_width + word_width <= width:
            current_line.append(word)
            current_width += word_width + break_width
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width + break_width
            else:
                lines.append(word)
                current_line = []
                current_width = 0

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def insert_multiline_text_on_image(
        image: Image,
        xy: tuple[float, float],
        size: tuple[float, float],
        lines: list[str],
        line_spacing: float,
        font: ImageFont,
) -> None:
    line_height = get_text_sizes('A', font)[1]

    draw = ImageDraw.Draw(image)
    y = xy[1] + (size[1] - len(lines) * line_height) // 2
    for line in lines:
        line_width = get_text_sizes(line, font)[0]
        x = xy[0] + (size[0] - line_width) // 2
        draw.text((x, y), line, font=font, fill='black')
        y += line_height + line_spacing


def insert_text_on_image(
        image: Image,
        xy: tuple[float, float],
        size: tuple[float, float],
        text: str,
        font: ImageFont,
):
    lines = split_text_to_lines(size[0], text, font)
    insert_multiline_text_on_image(image, xy, size, lines, 5, font)
    return image


def fetch_meme_image(meme: MemeTemplateProps) -> Image:
    response = httpx.get(meme.image_src)
    response.raise_for_status()

    image = Image.open(BytesIO(response.content))
    image.thumbnail((meme.image_width, meme.image_height))

    return image


def image2bytes(image: Image) -> bytes:
    img = BytesIO()
    image.save(img, format=image.format or 'PNG')

    return img.getvalue()


async def generate_meme(
        session: AsyncSession,
        scream_id: int,
) -> bytes:
    scream = await get_scream(session, scream_id)

    supermeme = Supermeme()
    meme_templates = await supermeme.search_meme_templates(scream.text)
    meme_template_props = await supermeme.get_meme_template_props(
        meme_templates[0]
    )

    image = fetch_meme_image(meme_template_props)
    caption = meme_template_props.initial_captions[0]

    insert_text_on_image(
        image=image,
        xy=(caption.x, caption.y),
        size=(caption.width, caption.height),
        text=scream.text,
        font=ImageFont.truetype(
            settings.memes.captions_font,
            caption.font_size
        ),
    )

    return image2bytes(image)
