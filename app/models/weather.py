from pydantic import BaseModel
from typing import Optional, List

class WeatherDataModel(BaseModel):
    station_id: str
    date: str
    max_temp: Optional[float]
    min_temp: Optional[float]
    precipitation: Optional[float]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "station_id": "USC00338552",
                "date": "1985-01-01",
                "max_temp": 15.6,
                "min_temp": 0.0,
                "precipitation": 5.8,
            }
        }


class WeatherStatsModel(BaseModel):
    station_id: str
    year: int
    avg_max_temp: Optional[float]
    avg_min_temp: Optional[float]
    total_precipitation: Optional[float]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "station_id": "USC00338552",
                "year": 1991,
                "avg_max_temp": 16.79,
                "avg_min_temp": 5.66,
                "total_precipitation": 712.3,
            }
        }
