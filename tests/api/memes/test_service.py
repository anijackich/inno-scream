import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO
from PIL import Image, ImageFont

from src.api.memes import service
from src.api.screams import schemas as scream_schemas
from src.api.external.supermeme import MemeTemplateProps, Caption


@pytest.fixture
def sample_image():
    img = Image.new('RGB', (300, 200), color='white')
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return img


@pytest.fixture
def sample_scream():
    return scream_schemas.Scream(
        scream_id=1,
        user_id=123,
        text='Test scream',
        created_at='2025-01-01T00:00:00',
        reactions={'👍': 5, '👎': 2},
    )


@pytest.fixture
def sample_meme_template_props():
    return MemeTemplateProps(
        pageTitle='Test Meme',
        imageSrc='https://example.com/meme.jpg',
        imageName='test_meme',
        imageDescription='Test meme description',
        imageWidth=300,
        imageHeight=200,
        initialCaptions=[
            Caption(
                x=10,
                y=10,
                text='',
                width=280,
                height=180,
                language='en',
                fontSize=20,
                fontFamily='Impact',
                rotateAngle=0,
            )
        ],
    )


@pytest.mark.asyncio
async def test_get_text_sizes():
    font = ImageFont.load_default()
    width, height = service.get_text_sizes('Test', font)

    assert width > 0
    assert height > 0


@pytest.mark.asyncio
async def test_split_text_to_lines():
    font = ImageFont.load_default()
    text = 'This is a test text that should be split into multiple lines'
    width = 100

    lines = service.split_text_to_lines(width, text, font)

    assert len(lines) > 1
    assert all(
        service.get_text_sizes(line, font)[0] <= width for line in lines
    )


@pytest.mark.asyncio
async def test_insert_multiline_text_on_image(sample_image):
    font = ImageFont.load_default()
    lines = ['Line 1', 'Line 2', 'Line 3']

    service.insert_multiline_text_on_image(
        image=sample_image,
        xy=(10, 10),
        size=(280, 180),
        lines=lines,
        line_spacing=5,
        font=font,
    )

    # No assertion needed, just checking it doesn't raise an exception


@pytest.mark.asyncio
async def test_insert_text_on_image(sample_image):
    font = ImageFont.load_default()
    text = 'This is a test text that should be split into multiple lines'

    result = service.insert_text_on_image(
        image=sample_image, xy=(10, 10), size=(280, 180), text=text, font=font
    )

    assert result is sample_image


@pytest.mark.asyncio
async def test_fetch_meme_image(sample_meme_template_props):
    mock_response = MagicMock()
    mock_response.content = b'test_image_data'
    mock_response.raise_for_status = MagicMock()

    with patch('src.api.memes.service.httpx.get', return_value=mock_response):
        with patch('src.api.memes.service.Image.open') as mock_open:
            mock_image = MagicMock()
            mock_open.return_value = mock_image

            result = service.fetch_meme_image(sample_meme_template_props)

            assert result is mock_image
            mock_image.thumbnail.assert_called_once_with(
                (
                    sample_meme_template_props.image_width,
                    sample_meme_template_props.image_height,
                )
            )


@pytest.mark.asyncio
async def test_image2bytes(sample_image):
    result = service.image2bytes(sample_image)

    assert isinstance(result, bytes)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_generate_meme(sample_scream, sample_meme_template_props):
    mock_get_scream = AsyncMock()
    mock_get_scream.return_value = sample_scream

    mock_supermeme = AsyncMock()
    mock_supermeme.search_meme_templates.return_value = ['test_meme']
    mock_supermeme.get_meme_template_props.return_value = (
        sample_meme_template_props
    )

    mock_fetch_image = MagicMock()
    mock_image = MagicMock()
    mock_fetch_image.return_value = mock_image

    mock_insert_text = MagicMock()
    mock_insert_text.return_value = mock_image

    mock_image2bytes = MagicMock()
    mock_image2bytes.return_value = b'test_meme_data'

    with patch('src.api.memes.service.get_scream', mock_get_scream):
        with patch(
            'src.api.memes.service.Supermeme', return_value=mock_supermeme
        ):
            with patch(
                'src.api.memes.service.fetch_meme_image', mock_fetch_image
            ):
                with patch(
                    'src.api.memes.service.insert_text_on_image',
                    mock_insert_text,
                ):
                    with patch(
                        'src.api.memes.service.image2bytes', mock_image2bytes
                    ):
                        with patch('src.api.memes.service.ImageFont.truetype'):
                            result = await service.generate_meme(
                                AsyncMock(), 1
                            )

                            assert result == b'test_meme_data'
                            mock_get_scream.assert_called_once()
                            mock_supermeme.search_meme_templates.assert_called_once_with(  # noqa: E501
                                sample_scream.text
                            )
                            mock_supermeme.get_meme_template_props.assert_called_once_with(  # noqa: E501
                                'test_meme'
                            )
                            mock_fetch_image.assert_called_once_with(
                                sample_meme_template_props
                            )
                            mock_insert_text.assert_called_once()
                            mock_image2bytes.assert_called_once_with(
                                mock_image
                            )
