from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Define the WeatherData ORM class
class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    max_temp = Column(Float, nullable=True)  # Max temperature in Celsius
    min_temp = Column(Float, nullable=True)  # Min temperature in Celsius
    precipitation = Column(Float, nullable=True)  # Precipitation in cm

    __table_args__ = (
        UniqueConstraint("station_id", "date", name="uq_weather_station_date"),
    )

    # Define relationship to WeatherStats
    stats = relationship(
        "WeatherStats",
        back_populates="weather_data",
        primaryjoin="WeatherData.station_id == foreign(WeatherStats.station_id)",
        viewonly=True,
    )


# Define the CropYieldData ORM class
class CropYieldData(Base):
    __tablename__ = "crop_yield_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(
        String, nullable=False
    )  # Assuming crop yield is linked to a station
    year = Column(Integer, nullable=False)
    yield_value = Column(
        Float, nullable=False
    )  # Renamed from 'yield' to 'yield_value' to avoid conflict with Python keyword

    __table_args__ = (
        UniqueConstraint("station_id", "year", name="uq_cropyield_station_year"),
    )


# Never needed this as a table, data should be dynamicly fetched and calulated: using a view instead

# Define the WeatherStats ORM class
# class WeatherStats(Base):
#     __tablename__ = 'weather_stats'

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     station_id = Column(String, ForeignKey("weather_data.station_id"), nullable=False)
#     year = Column(Integer, nullable=False)
#     avg_max_temp = Column(Float, nullable=True)
#     avg_min_temp = Column(Float, nullable=True)
#     total_precipitation = Column(Float, nullable=True)

#     __table_args__ = (
#         UniqueConstraint('station_id', 'year', name='uq_weatherstats_station_year'),
#     )

#     # Define relationship to WeatherData
#     weather_data = relationship(
#         "WeatherData",
#         back_populates="stats",
#         remote_side="WeatherData.station_id",
#         viewonly=True
#     )
