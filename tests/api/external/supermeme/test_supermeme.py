import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from src.api.external.supermeme.supermeme import Supermeme, MemeTemplate, MemeTemplateProps, Caption


@pytest.fixture
def sample_meme_template():
    return MemeTemplate(
        name="test_meme",
        image_path="/path/to/image.jpg",
        description="Test meme description",
        meme_text="Test meme text"
    )


@pytest.fixture
def sample_meme_template_props():
    return MemeTemplateProps(
        pageTitle="Test Meme",
        imageSrc="https://example.com/meme.jpg",
        imageName="test_meme",
        imageDescription="Test meme description",
        imageWidth=300,
        imageHeight=200,
        initialCaptions=[
            Caption(
                x=10,
                y=10,
                text="",
                width=280,
                height=180,
                language="en",
                fontSize=20,
                fontFamily="Impact",
                rotateAngle=0
            )
        ]
    )


@pytest.fixture
def sample_next_data(sample_meme_template_props):
    return {
        "props": {
            "pageProps": sample_meme_template_props.model_dump(by_alias=True)
        }
    }


@pytest.mark.asyncio
async def test_supermeme_init():
    supermeme = Supermeme()
    assert supermeme.client is not None
    assert supermeme.client.base_url == "https://supermeme.ai"
    
    custom_url = "https://custom-supermeme.example.com"
    custom_timeout = 60.0
    supermeme_custom = Supermeme(base_url=custom_url, timeout=custom_timeout)
    assert supermeme_custom.client.base_url == custom_url
    assert supermeme_custom.client.timeout.connect == custom_timeout


@pytest.mark.asyncio
async def test_search_meme_templates(sample_meme_template):
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={
        "memeTemplates": [sample_meme_template.model_dump()]
    })
    mock_response.raise_for_status = AsyncMock()
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    with patch("src.api.external.supermeme.supermeme.AsyncClient", return_value=mock_client):
        with patch("src.api.external.supermeme.supermeme.MemeTemplate.model_validate") as mock_validate:
            mock_validate.return_value = sample_meme_template
            supermeme = Supermeme()
            result = await supermeme.search_meme_templates("test query")
        
        assert len(result) == 1
        assert isinstance(result[0], MemeTemplate)
        assert result[0].name == sample_meme_template.name
        assert result[0].image_path == sample_meme_template.image_path
        assert result[0].description == sample_meme_template.description
        assert result[0].meme_text == sample_meme_template.meme_text
        
        mock_client.get.assert_called_once_with(
            '/api/search',
            params={'searchQuery': 'test query'},
        )
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_search_meme_templates_invalid_json():
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    mock_response.raise_for_status = AsyncMock()
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    with patch("src.api.external.supermeme.supermeme.AsyncClient", return_value=mock_client):
        supermeme = Supermeme()
        with pytest.raises(ValueError):
            await supermeme.search_meme_templates("test query")


@pytest.mark.asyncio
async def test_get_meme_template_props(sample_meme_template, sample_next_data):
    mock_response = AsyncMock()
    mock_response.content = b"<html><body><script id='__NEXT_DATA__'>" + json.dumps(sample_next_data).encode() + b"</script></body></html>"
    mock_response.raise_for_status = AsyncMock()
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    with patch("src.api.external.supermeme.supermeme.AsyncClient", return_value=mock_client):
        with patch("src.api.external.supermeme.supermeme.print"):  # Suppress print statement
            supermeme = Supermeme()
            result = await supermeme.get_meme_template_props(sample_meme_template)
            
            assert isinstance(result, MemeTemplateProps)
            assert result.page_title == "Test Meme"
            assert result.image_src == "https://example.com/meme.jpg"
            assert result.image_name == "test_meme"
            assert result.image_description == "Test meme description"
            assert result.image_width == 300
            assert result.image_height == 200
            assert len(result.initial_captions) == 1
            
            mock_client.get.assert_called_once_with(f'/meme/{sample_meme_template.name}')
            mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_meme_template_props_no_next_data():
    mock_response = AsyncMock()
    mock_response.content = b"<html><body></body></html>"
    mock_response.raise_for_status = AsyncMock()
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    with patch("src.api.external.supermeme.supermeme.AsyncClient", return_value=mock_client):
        supermeme = Supermeme()
        with pytest.raises(ValueError, match="No data found"):
            await supermeme.get_meme_template_props(MagicMock())


@pytest.mark.asyncio
async def test_get_meme_template_props_invalid_schema():
    mock_response = AsyncMock()
    mock_response.content = b"<html><body><script id='__NEXT_DATA__'>{\"props\":{}}</script></body></html>"
    mock_response.raise_for_status = AsyncMock()
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    with patch("src.api.external.supermeme.supermeme.AsyncClient", return_value=mock_client):
        with patch("src.api.external.supermeme.supermeme.print"):  # Suppress print statement
            supermeme = Supermeme()
            with pytest.raises(ValueError, match="Invalid __NEXT_DATA__ schema"):
                await supermeme.get_meme_template_props(MagicMock())


@pytest.mark.asyncio
async def test_caption_model():
    caption = Caption(
        x=10,
        y=10,
        text="Test caption",
        width=280,
        height=180,
        language="en",
        fontSize=20,
        fontFamily="Impact",
        rotateAngle=0
    )
    
    assert caption.x == 10
    assert caption.y == 10
    assert caption.text == "Test caption"
    assert caption.width == 280
    assert caption.height == 180
    assert caption.language == "en"
    assert caption.font_size == 20
    assert caption.font_family == "Impact"
    assert caption.rotate_angle == 0


@pytest.mark.asyncio
async def test_meme_template_model():
    template = MemeTemplate(
        name="test_meme",
        image_path="/path/to/image.jpg",
        description="Test meme description",
        meme_text="Test meme text"
    )
    
    assert template.name == "test_meme"
    assert template.image_path == "/path/to/image.jpg"
    assert template.description == "Test meme description"
    assert template.meme_text == "Test meme text"


@pytest.mark.asyncio
async def test_meme_template_props_model(sample_meme_template_props):
    assert sample_meme_template_props.page_title == "Test Meme"
    assert sample_meme_template_props.image_src == "https://example.com/meme.jpg"
    assert sample_meme_template_props.image_name == "test_meme"
    assert sample_meme_template_props.image_description == "Test meme description"
    assert sample_meme_template_props.image_width == 300
    assert sample_meme_template_props.image_height == 200
    assert len(sample_meme_template_props.initial_captions) == 1
    assert sample_meme_template_props.initial_captions[0].x == 10
    assert sample_meme_template_props.initial_captions[0].y == 10