from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, column, text
from app.db.database import get_db
from app.models.weather import WeatherDataModel, WeatherStatsModel
from typing import List
import pandas as pd
import logging

router = APIRouter()

@router.get(
    "/weather",
    response_model=List[WeatherDataModel],
    summary="Retrieve Weather Data",
    description=(
        "Fetch raw weather data records with optional filters, sorting, "
        "and pagination. You can filter by station ID, date range, or order results."
    ),
    tags=["Weather Data"],
    responses={
        200: {
            "description": "A list of weather data records.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "station_id": "USC00338552",
                            "date": "1985-01-01",
                            "max_temp": 15.6,
                            "min_temp": 0.0,
                            "precipitation": 5.8,
                        }
                    ]
                }
            },
        },
        400: {"description": "Invalid query parameters."},
        500: {"description": "Internal server error."},
    },
)
async def get_weather_data(
    station_id: str = Query(None, description="Filter by station ID"),
    start_date: str = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    order_by: str = Query("date", description="Field to order by (e.g., date, max_temp)"),
    order_direction: str = Query("asc", description="Order direction (asc or desc)"),
    session: AsyncSession = Depends(get_db),
):

    """
    Retrieve raw weather data with optional filters, pagination, and sorting.
    """
    try:
        query = select(column("station_id"), column("date"), column("max_temp"), column("min_temp"), column("precipitation")).select_from(text("weather_data"))

        if station_id:
            query = query.where(column("station_id") == station_id)
        if start_date:
            query = query.where(column("date") >= start_date)
        if end_date:
            query = query.where(column("date") <= end_date)

        query = query.offset(offset).limit(limit)
        results = (await session.execute(query)).fetchall()
        return [
          WeatherDataModel.from_row(row)  # Use the `from_row` method to handle serialization
          for row in results
        ]

    except Exception as e:
        logging.error(f"Error retrieving weather data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")








@router.get(
    "/weather/stats",
    response_model=List[WeatherStatsModel],
    summary="Retrieve Weather Statistics",
    description=(
        "Fetch aggregated weather statistics dynamically generated from the "
        "database view. Statistics include average max/min temperatures and total "
        "precipitation for each station and year."
    ),
    tags=["Weather Statistics"],
    responses={
        200: {
            "description": "A list of weather statistics.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "station_id": "USC00338552",
                            "year": 1991,
                            "avg_max_temp": 16.79,
                            "avg_min_temp": 5.66,
                            "total_precipitation": 712.3,
                        }
                    ]
                }
            },
        },
        400: {"description": "Invalid query parameters."},
        500: {"description": "Internal server error."},
    },
)
async def get_weather_stats(
    station_id: str = Query(None, description="Filter by station ID"),
    year: int = Query(None, description="Filter by year"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    session: AsyncSession = Depends(get_db),
):
    """
    Retrieve aggregated weather statistics dynamically from the view.
    """
    try:
        query = select(
            column("station_id"),
            column("year"),
            column("avg_max_temp"),
            column("avg_min_temp"),
            column("total_precipitation"),
        ).select_from(text("weather_stats_view"))

        if station_id:
            query = query.where(column("station_id") == station_id)
        if year:
            query = query.where(column("year") == year)

        query = query.offset(offset).limit(limit)
        results = (await session.execute(query)).fetchall()

        # Convert rows into models while filtering out invalid float values
        def sanitize_float(value):
            return value if value is not None and not (pd.isna(value) or value in [float('inf'), float('-inf')]) else None

        return [
            WeatherStatsModel(
                station_id=row.station_id,
                year=row.year,
                avg_max_temp=sanitize_float(row.avg_max_temp),
                avg_min_temp=sanitize_float(row.avg_min_temp),
                total_precipitation=sanitize_float(row.total_precipitation),
            )
            for row in results
        ]

    except Exception as e:
        logging.error(f"Error retrieving weather stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
