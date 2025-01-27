# tests/test_crop_yield_etl.py

import pytest
import pandas as pd
from app.etl.impl_crop_yield_etl import CropYieldETL
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock
from pandas.api.types import is_integer_dtype


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def crop_yield_etl(session):
    return CropYieldETL(session=session)


@pytest.fixture
def crop_yield_file_content():
    """
    Simulated binary content of a crop yield file.
    """
    return b"2023\t150\n2022\t145\n"


def test_crop_yield_etl_extract(crop_yield_etl, crop_yield_file_content):
    """
    Test the extract method of CropYieldETL.
    """
    df = crop_yield_etl.extract(crop_yield_file_content, "crop_yield.txt")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert df.columns.tolist() == ["year", "yield_value", "station_id"]


def test_crop_yield_etl_transform(crop_yield_etl):
    """
    Test the transform method of CropYieldETL.
    """
    # Updated raw_data to use 'yield_value' and include 'station_id'
    raw_data = pd.DataFrame(
        {
            "year": [2023, 2022],
            "yield_value": [150, 145],
            "station_id": ["station1", "station2"],
        }
    )
    transformed_data = crop_yield_etl.transform(raw_data)
    assert not transformed_data.empty
    assert is_integer_dtype(
        transformed_data["year"]
    )  # Check if column is integer dtype
    assert transformed_data["yield_value"].dtype == "float64"


@pytest.mark.asyncio
async def test_crop_yield_etl_load(crop_yield_etl):
    """
    Test the load method of CropYieldETL with mock data.
    """
    transformed_data = pd.DataFrame(
        {
            "year": [2023, 2022],
            "yield_value": [150.0, 145.0],  # Use yield_value instead of yield
            "station_id": ["station1", "station2"],
        }
    )

    await crop_yield_etl.load(transformed_data)

    # Verify that the session.execute method was called
    assert crop_yield_etl.session.execute.called
    assert crop_yield_etl.session.commit.called
