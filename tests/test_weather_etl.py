# tests/test_weather_etl.py

import pytest
import pandas as pd
from app.etl.impl_weather_etl import WeatherETL
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def weather_etl(session):
    return WeatherETL(session=session)


@pytest.fixture
def weather_file_content():
    """
    Simulated binary content of a weather file.
    """
    return b"20230101\t100\t-50\t5\n20230102\t110\t-40\t0\n"


def test_weather_etl_extract(weather_etl, weather_file_content):
    """
    Test the extract method of WeatherETL.
    """
    df = weather_etl.extract(weather_file_content, "USC00110072.txt")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.columns.tolist() == [
        "date",
        "max_temp",
        "min_temp",
        "precipitation",
        "station_id",
    ]


def test_weather_etl_transform(weather_etl):
    """
    Test the transform method of WeatherETL.
    """
    raw_data = pd.DataFrame(
        {
            "date": ["20230101", "20230102"],
            "max_temp": [100, 110],
            "min_temp": [-50, -40],
            "precipitation": [5, 0],
            "station_id": ["USC00110072", "USC00110072"],
        }
    )
    transformed_data = weather_etl.transform(raw_data)
    assert not transformed_data.empty
    assert "date" in transformed_data.columns
    assert transformed_data["max_temp"].iloc[0] == 10.0
    assert transformed_data["precipitation"].iloc[1] == 0.0


@pytest.mark.asyncio
async def test_weather_etl_load(weather_etl):
    """
    Test the load method of WeatherETL with mock data.
    """
    transformed_data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2023-01-01", "2023-01-02"]),
            "max_temp": [10.0, 11.0],
            "min_temp": [-5.0, -4.0],
            "precipitation": [0.5, 0.0],
            "station_id": ["USC00110072", "USC00110072"],
        }
    )

    await weather_etl.load(transformed_data)

    # Verify that the session.execute method was called
    assert weather_etl.session.execute.called
    assert weather_etl.session.commit.called
