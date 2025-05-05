from typing import List, Any
from pydantic import BaseModel
from httpx import AsyncClient


class Dataset(BaseModel):
    """
    Labelled list of values.

    Attributes:
        label: Name of the dataset
        data: Values of the dataset
        backgroundColor: Background color of the dataset
    """
    label: str
    data: List[float]
    backgroundColor: str | None = None


class ChartData(BaseModel):
    """
    Chart data with chart labels and datasets.

    Attributes:
        labels: List of labels (names for points on x-axis)
        datasets: Datasets
    """
    labels: List[str]
    datasets: List[Dataset]


class Chart(BaseModel):
    """
    Chart

    Attributes:
        type: Chart type ("line", "bar", ...).
            See https://www.chartjs.org/docs/latest/
        data: Chart Data
        options: Chart options
    """
    type: str
    data: ChartData
    options: dict[str, Any] | None = None


class QuickChart:
    """
    Wrapper class for QuickChart API

    Example:
        ```python
        quickchart = QuickChart()
        chart = Chart(
            type="line",
            data=ChartData(
                labels=["Mon", "Tue", "Wed"],
                datasets=[
                    Dataset(
                        label="posts",
                        data=[34, 79, 22]
                    )
                ]
            )
        )
        image = await quickchart.chart(chart)
        ```
    """

    def __init__(self, quickchart_url: str = "https://quickchart.io"):
        """
        Initialize a QuickChart instance.

        Args:
            quickchart_url (str): Base url of QuickChart API.
        """
        self.client = AsyncClient(base_url=quickchart_url)

    async def chart(self, chart: Chart) -> bytes:
        """
        Creates a chart image.

        Args:
            chart (Chart): Chart configuration object.

        Returns:
            bytes: Chart image data as bytes

        Raises:
            httpx.HTTPStatusError
            httpx.RequestError
            httpx.TimeoutException
            https.NetworkError
        """
        response = await self.client.post("/chart", json={
            "chart": chart.model_dump_json(),
            "backgroundColor": "white"
        })
        response.raise_for_status()
        return response.content
