import pytest
from unittest.mock import AsyncMock, patch

from src.api.external.quickchart.quickchart import QuickChart, Chart, ChartData, Dataset


@pytest.fixture
def sample_chart():
    return Chart(
        type="bar",
        data=ChartData(
            labels=["Mon", "Tue", "Wed"],
            datasets=[
                Dataset(
                    label="posts",
                    data=[34, 79, 22],
                    backgroundColor="black"
                )
            ]
        ),
        options={
            "legend": {
                "display": False
            }
        }
    )


@pytest.mark.asyncio
async def test_quickchart_init():
    quickchart = QuickChart()
    assert quickchart.client is not None
    assert quickchart.client.base_url == "https://quickchart.io"
    
    custom_url = "https://custom-quickchart.example.com"
    quickchart_custom = QuickChart(quickchart_url=custom_url)
    assert quickchart_custom.client.base_url == custom_url


@pytest.mark.asyncio
async def test_chart(sample_chart):
    mock_response = AsyncMock()
    mock_response.content = b"test_chart_data"
    mock_response.raise_for_status = AsyncMock()
    
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    
    with patch("src.api.external.quickchart.quickchart.AsyncClient", return_value=mock_client):
        quickchart = QuickChart()
        result = await quickchart.chart(sample_chart)
        
        assert result == b"test_chart_data"
        mock_client.post.assert_called_once_with("/chart", json={
            "chart": sample_chart.model_dump_json(),
            "backgroundColor": "white"
        })
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_dataset_model():
    dataset = Dataset(
        label="posts",
        data=[34, 79, 22],
        backgroundColor="black"
    )
    
    assert dataset.label == "posts"
    assert dataset.data == [34, 79, 22]
    assert dataset.backgroundColor == "black"


@pytest.mark.asyncio
async def test_chart_data_model():
    chart_data = ChartData(
        labels=["Mon", "Tue", "Wed"],
        datasets=[
            Dataset(
                label="posts",
                data=[34, 79, 22],
                backgroundColor="black"
            )
        ]
    )
    
    assert chart_data.labels == ["Mon", "Tue", "Wed"]
    assert len(chart_data.datasets) == 1
    assert chart_data.datasets[0].label == "posts"


@pytest.mark.asyncio
async def test_chart_model():
    chart = Chart(
        type="bar",
        data=ChartData(
            labels=["Mon", "Tue", "Wed"],
            datasets=[
                Dataset(
                    label="posts",
                    data=[34, 79, 22],
                    backgroundColor="black"
                )
            ]
        ),
        options={
            "legend": {
                "display": False
            }
        }
    )
    
    assert chart.type == "bar"
    assert chart.data.labels == ["Mon", "Tue", "Wed"]
    assert chart.options == {"legend": {"display": False}}