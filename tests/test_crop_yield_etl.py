# tests/test_crop_yield_etl.py
import pytest
from unittest.mock import AsyncMock, MagicMock
import pandas as pd
from app.etl.impl_crop_yield_etl import CropYieldETL
from app.db.schema import CropYieldData

@pytest.fixture
def sample_crop_yield_data():
    # Sample tab-separated crop yield data without headers
    data = """1985\t225447
1986\t208944
1987\t181143
1988\t125194
1989\t191320
1990\t201534
1991\t189868
1992\t240719
1993\t160986
1994\t255295
1995\t187970
1996\t234518
1997\t233864
1998\t247882
1999\t239549
2000\t251854
2001\t241377
2002\t227767
2003\t256229
2004\t299876
2005\t282263
2006\t267503
2007\t331177
2008\t305911
2009\t331921
2010\t315618
2011\t312789
2012\t273192
2013\t351272
2014\t361091"""
    return data.encode('utf-8')

@pytest.fixture
def filename_crop_yield():
    return "stationXYZ.txt"

@pytest.mark.asyncio
async def test_crop_yield_etl_extract(sample_crop_yield_data, filename_crop_yield):
    # Create an instance of CropYieldETL with a mock session
    mock_session = MagicMock()
    etl = CropYieldETL(session=mock_session)
    
    df = etl.extract(sample_crop_yield_data, filename_crop_yield)
    
    expected_data = {
        "year": [1985.0, 1986.0, 1987.0, 1988.0, 1989.0, 1990.0, 1991.0, 1992.0, 1993.0,
                 1994.0, 1995.0, 1996.0, 1997.0, 1998.0, 1999.0, 2000.0, 2001.0, 2002.0,
                 2003.0, 2004.0, 2005.0, 2006.0, 2007.0, 2008.0, 2009.0, 2010.0, 2011.0,
                 2012.0, 2013.0, 2014.0],
        "yield_value": [225447.0, 208944.0, 181143.0, 125194.0, 191320.0, 201534.0,
                        189868.0, 240719.0, 160986.0, 255295.0, 187970.0, 234518.0,
                        233864.0, 247882.0, 239549.0, 251854.0, 241377.0, 227767.0,
                        256229.0, 299876.0, 282263.0, 267503.0, 331177.0, 305911.0,
                        331921.0, 315618.0, 312789.0, 273192.0, 351272.0, 361091.0],
        "station_id": ["stationXYZ"] * 30
    }
    expected_df = pd.DataFrame(expected_data)
    
    pd.testing.assert_frame_equal(df.reset_index(drop=True), expected_df)

@pytest.mark.asyncio
async def test_crop_yield_etl_transform():
    # Sample raw DataFrame
    raw_data = {
        "year": [1985.0, 1986.0, 1987.0, 1988.0, 1989.0],
        "yield_value": [225447.0, 208944.0, 181143.0, 125194.0, 191320.0],
        "station_id": ["stationXYZ"] * 5
    }
    df_raw = pd.DataFrame(raw_data)
    
    # Create an instance of CropYieldETL with a mock session
    mock_session = MagicMock()
    etl = CropYieldETL(session=mock_session)
    
    df_transformed = etl.transform(df_raw)
    
    # Expected transformation: data is already clean
    pd.testing.assert_frame_equal(df_transformed.reset_index(drop=True), df_raw)

@pytest.mark.asyncio
async def test_crop_yield_etl_load():
    # Sample transformed DataFrame
    transformed_data = {
        "year": [1985, 1986, 1987, 1988, 1989],
        "yield_value": [225447.0, 208944.0, 181143.0, 125194.0, 191320.0],
        "station_id": ["stationXYZ"] * 5
    }
    df_transformed = pd.DataFrame(transformed_data)
    
    # Create a mock AsyncSession
    mock_session = AsyncMock()
    
    # Create an instance of CropYieldETL
    etl = CropYieldETL(session=mock_session, batch_size=2)
    
    await etl.load(df_transformed)
    
    # Verify that execute and commit are called three times (batches of 2, 2, and 1)
    assert mock_session.execute.call_count == 3
    assert mock_session.commit.call_count == 3
    
    # Verify that the correct SQL statements were prepared
    insert_calls = mock_session.execute.call_args_list
    first_batch = df_transformed.iloc[:2].to_dict(orient="records")
    second_batch = df_transformed.iloc[2:4].to_dict(orient="records")
    third_batch = df_transformed.iloc[4:].to_dict(orient="records")
    
    # Check first batch
    stmt1 = insert(CropYieldData).values(first_batch)
    stmt1 = stmt1.on_conflict_do_nothing(index_elements=['station_id', 'year'])
    mock_session.execute.assert_any_call(stmt1)
    
    # Check second batch
    stmt2 = insert(CropYieldData).values(second_batch)
    stmt2 = stmt2.on_conflict_do_nothing(index_elements=['station_id', 'year'])
    mock_session.execute.assert_any_call(stmt2)
    
    # Check third batch
    stmt3 = insert(CropYieldData).values(third_batch)
    stmt3 = stmt3.on_conflict_do_nothing(index_elements=['station_id', 'year'])
    mock_session.execute.assert_any_call(stmt3)
