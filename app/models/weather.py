from pydantic import BaseModel
from typing import Optional, List

class WeatherDataModel(BaseModel):
    station_id: str
    date: str  # Keep this as a string for JSON serialization
    max_temp: Optional[float]
    min_temp: Optional[float]
    precipitation: Optional[float]

    class Config:
        from_attributes = True  # Use this instead of orm_mode in Pydantic v2
        json_schema_extra = {
            "example": {
                "station_id": "USC00338552",
                "date": "1985-01-01",
                "max_temp": 15.6,
                "min_temp": 0.0,
                "precipitation": 5.8,
            }
        }

    @classmethod
    def from_row(cls, row):
        # Convert database row into a valid Pydantic model
        return cls(
            station_id=row.station_id,
            date=row.date.isoformat() if row.date else None,  # Ensure date is a string
            max_temp=row.max_temp,
            min_temp=row.min_temp,
            precipitation=row.precipitation,
        )


class WeatherStatsModel(BaseModel):
    station_id: str
    year: int
    avg_max_temp: Optional[float]
    avg_min_temp: Optional[float]
    total_precipitation: Optional[float]

    class Config:
        from_attributes = True  # Use this instead of orm_mode in Pydantic v2
        json_schema_extra = {
            "example": {
                "station_id": "USC00338552",
                "year": 1991,
                "avg_max_temp": 16.79,
                "avg_min_temp": 5.66,
                "total_precipitation": 712.3,
            }
        }

    @classmethod
    def from_row(cls, row):
        # Convert database row into a valid Pydantic model
        return cls(
            station_id=row.station_id,
            year=row.year,
            avg_max_temp=row.avg_max_temp,
            avg_min_temp=row.avg_min_temp,
            total_precipitation=row.total_precipitation,
        )
