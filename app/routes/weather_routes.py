from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc
from sqlalchemy.sql import text, column
from app.db.schema import WeatherData
from app.db.database import get_db
import logging

router = APIRouter()


@router.get("/weather")
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
        # Base query
        query = select(WeatherData)

        # Apply filters
        if station_id:
            query = query.where(WeatherData.station_id == station_id)
        if start_date:
            query = query.where(WeatherData.date >= start_date)
        if end_date:
            query = query.where(WeatherData.date <= end_date)

        # Create total records query (without order_by)
        total_records_query = query.with_only_columns(func.count())
        total_records = (await session.execute(total_records_query)).scalar()

        # Apply sorting
        order_column = getattr(WeatherData, order_by, None)
        if not order_column:
            raise HTTPException(status_code=400, detail=f"Invalid order_by field: {order_by}")

        if order_direction.lower() == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        # Apply pagination
        query = query.offset(offset).limit(limit)
        results = (await session.execute(query)).scalars().all()

        return {
            "total_records": total_records,
            "limit": limit,
            "offset": offset,
            "data": [result.__dict__ for result in results],
        }

    except Exception as e:
        logging.error(f"Error retrieving weather data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


from math import isnan, isinf

@router.get("/weather/stats")
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
        # Base query for the view
        base_query = select(
            column("station_id"),
            column("year"),
            column("avg_max_temp"),
            column("avg_min_temp"),
            column("total_precipitation"),
        ).select_from(text("weather_stats_view"))

        # Apply filters
        if station_id:
            base_query = base_query.where(column("station_id") == station_id)
        if year:
            base_query = base_query.where(column("year") == year)

        # Get total records count
        total_records_query = base_query.with_only_columns(func.count())
        total_records = (await session.execute(total_records_query)).scalar()

        # Apply pagination to the base query
        paginated_query = base_query.offset(offset).limit(limit)
        results = (await session.execute(paginated_query)).fetchall()

        # Sanitize and format results
        def sanitize_value(value):
            """Replace NaN and Infinity values with None."""
            if value is None or isinstance(value, (int, float)) and (isnan(value) or isinf(value)):
                return None
            return value

        data = [
            {
                "station_id": row.station_id,
                "year": int(row.year),
                "avg_max_temp": sanitize_value(row.avg_max_temp),
                "avg_min_temp": sanitize_value(row.avg_min_temp),
                "total_precipitation": sanitize_value(row.total_precipitation),
            }
            for row in results
        ]

        return {
            "total_records": total_records,
            "limit": limit,
            "offset": offset,
            "data": data,
        }

    except Exception as e:
        logging.error(f"Error retrieving weather stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
