# tests/test_weather_etl.py
import pytest
from unittest.mock import AsyncMock, MagicMock
import pandas as pd
from app.etl.impl_weather_etl import WeatherETL
from app.db.schema import WeatherData

@pytest.fixture
def sample_weather_data():
    # Sample tab-separated weather data without headers
    data = """20200101\t250\t150\t50
20200102\t260\t160\t60
20200103\t270\t170\t70"""
    return data.encode('utf-8')

@pytest.fixture
def filename_weather():
    return "stationABC.txt"

@pytest.mark.asyncio
async def test_weather_etl_extract(sample_weather_data, filename_weather):
    # Create an instance of WeatherETL with a mock session
    mock_session = MagicMock()
    etl = WeatherETL(session=mock_session)
    
    df = etl.extract(sample_weather_data, filename_weather)
    
    expected_data = {
        "date": ["20200101", "20200102", "20200103"],
        "max_temp": [250.0, 260.0, 270.0],
        "min_temp": [150.0, 160.0, 170.0],
        "precipitation": [50.0, 60.0, 70.0],
        "station_id": ["stationABC"] * 3
    }
    expected_df = pd.DataFrame(expected_data)
    
    pd.testing.assert_frame_equal(df.reset_index(drop=True), expected_df)

@pytest.mark.asyncio
async def test_weather_etl_transform():
    # Sample raw DataFrame
    raw_data = {
        "date": ["2020-01-01", "2020-01-02", "2020-01-03"],
        "max_temp": [25.0, 26.0, 27.0],
        "min_temp": [15.0, 16.0, 17.0],
        "precipitation": [5.0, 6.0, 7.0]
    }
    df_raw = pd.DataFrame(raw_data)
    
    # Create an instance of WeatherETL with a mock session
    mock_session = MagicMock()
    etl = WeatherETL(session=mock_session)
    
    df_transformed = etl.transform(df_raw)
    
    # Expected transformation: data is already clean
    pd.testing.assert_frame_equal(df_transformed.reset_index(drop=True), df_raw)

@pytest.mark.asyncio
async def test_weather_etl_load():
    # Sample transformed DataFrame
    transformed_data = {
        "date": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-02"), pd.Timestamp("2020-01-03")],
        "max_temp": [25.0, 26.0, 27.0],
        "min_temp": [15.0, 16.0, 17.0],
        "precipitation": [5.0, 6.0, 7.0],
        "station_id": ["stationABC"] * 3
    }
    df_transformed = pd.DataFrame(transformed_data)
    
    # Create a mock AsyncSession
    mock_session = AsyncMock()
    
    # Create an instance of WeatherETL
    etl = WeatherETL(session=mock_session, batch_size=2)
    
    await etl.load(df_transformed)
    
    # Verify that execute and commit are called twice (batches of 2 and 1)
    assert mock_session.execute.call_count == 2
    assert mock_session.commit.call_count == 2
    
    # Verify that the correct SQL statements were prepared
    insert_calls = mock_session.execute.call_args_list
    first_batch = df_transformed.iloc[:2].to_dict(orient="records")
    second_batch = df_transformed.iloc[2:].to_dict(orient="records")
    
    # Check first batch
    stmt1 = insert(WeatherData).values(first_batch)
    stmt1 = stmt1.on_conflict_do_nothing(index_elements=['station_id', 'date'])
    mock_session.execute.assert_any_call(stmt1)
    
    # Check second batch
    stmt2 = insert(WeatherData).values(second_batch)
    stmt2 = stmt2.on_conflict_do_nothing(index_elements=['station_id', 'date'])
    mock_session.execute.assert_any_call(stmt2)
