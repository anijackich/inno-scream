import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from httpx import Response

from src.bot.services.innoscream.client import InnoScreamAPI
from src.bot.services.innoscream.models import Scream, Stats


@pytest.fixture
def mock_client():
    with patch(
        'src.bot.services.innoscream.client.AsyncClient'
    ) as mock_client:
        client_instance = mock_client.return_value
        client_instance.post = AsyncMock()
        client_instance.get = AsyncMock()
        client_instance.delete = AsyncMock()
        yield client_instance


@pytest.fixture
def api(mock_client):
    return InnoScreamAPI(base_url='http://test-api.com')


@pytest.fixture
def sample_scream_data():
    return {
        'scream_id': 1,
        'user_id': 123,
        'text': 'Test scream',
        'created_at': datetime.now().isoformat(),
        'reactions': {'👍': 5, '👎': 2},
    }


@pytest.fixture
def sample_stats_data():
    return {'screams_count': 10, 'reactions_count': {'👍': 15, '👎': 5}}


@pytest.mark.asyncio
async def test_create_scream(api, mock_client, sample_scream_data):
    mock_response = Response(200, json=sample_scream_data)
    mock_response.raise_for_status = lambda: None
    mock_client.post.return_value = mock_response

    result = await api.create_scream(user_id=123, text='Test scream')

    mock_client.post.assert_called_once_with(
        '/screams', json={'user_id': 123, 'text': 'Test scream'}
    )
    assert isinstance(result, Scream)
    assert result.scream_id == sample_scream_data['scream_id']
    assert result.user_id == sample_scream_data['user_id']
    assert result.text == sample_scream_data['text']
    assert result.reactions == sample_scream_data['reactions']


@pytest.mark.asyncio
async def test_get_scream(api, mock_client, sample_scream_data):
    mock_response = Response(200, json=sample_scream_data)
    mock_response.raise_for_status = lambda: None
    mock_client.get.return_value = mock_response

    result = await api.get_scream(scream_id=1)

    mock_client.get.assert_called_once_with('/screams/1')
    assert isinstance(result, Scream)
    assert result.scream_id == sample_scream_data['scream_id']


@pytest.mark.asyncio
async def test_delete_scream(api, mock_client):
    mock_response = Response(204)
    mock_response.raise_for_status = lambda: None
    mock_client.delete.return_value = mock_response

    await api.delete_scream(scream_id=1)

    mock_client.delete.assert_called_once_with('/screams/1')


@pytest.mark.asyncio
async def test_react_on_scream(api, mock_client, sample_scream_data):
    mock_response = Response(200, json=sample_scream_data)
    mock_response.raise_for_status = lambda: None
    mock_client.post.return_value = mock_response

    result = await api.react_on_scream(scream_id=1, user_id=123, reaction='👍')

    mock_client.post.assert_called_once_with(
        '/screams/1/react',
        json={'scream_id': 1, 'user_id': 123, 'reaction': '👍'},
    )
    assert isinstance(result, Scream)
    assert result.scream_id == sample_scream_data['scream_id']


@pytest.mark.asyncio
async def test_get_stats(api, mock_client, sample_stats_data):
    mock_response = Response(200, json=sample_stats_data)
    mock_response.raise_for_status = lambda: None
    mock_client.get.return_value = mock_response

    result = await api.get_stats(user_id=123)

    mock_client.get.assert_called_once_with('/analytics/123/stats')
    assert isinstance(result, Stats)
    assert result.screams_count == sample_stats_data['screams_count']
    assert result.reactions_count == sample_stats_data['reactions_count']


@pytest.mark.asyncio
async def test_get_graph(api, mock_client):
    mock_content = b'graph_image_bytes'
    mock_response = Response(200, content=mock_content)
    mock_response.raise_for_status = lambda: None
    mock_client.get.return_value = mock_response

    result = await api.get_graph(user_id=123, period='week')

    mock_client.get.assert_called_once_with(
        '/analytics/123/graph', params={'period': 'week'}
    )
    assert result == mock_content


@pytest.mark.asyncio
async def test_get_most_voted_scream(api, mock_client, sample_scream_data):
    mock_response = Response(200, json=sample_scream_data)
    mock_response.raise_for_status = lambda: None
    mock_client.get.return_value = mock_response

    result = await api.get_most_voted_scream(period='day')

    mock_client.get.assert_called_once_with(
        '/analytics/getMostVoted', params={'period': 'day'}
    )
    assert isinstance(result, Scream)
    assert result.scream_id == sample_scream_data['scream_id']


@pytest.mark.asyncio
async def test_get_most_voted_scream_empty(api, mock_client):
    mock_response = Response(200, content=b'')
    mock_response.raise_for_status = lambda: None
    mock_client.get.return_value = mock_response

    result = await api.get_most_voted_scream(period='day')

    assert result is None


@pytest.mark.asyncio
async def test_generate_meme(api, mock_client):
    mock_content = b'meme_image_bytes'
    mock_response = Response(200, content=mock_content)
    mock_response.raise_for_status = lambda: None
    mock_client.post.return_value = mock_response

    result = await api.generate_meme(scream_id=1)

    mock_client.post.assert_called_once_with(
        '/memes/generate', params={'scream_id': 1}, timeout=60
    )
    assert result == mock_content
