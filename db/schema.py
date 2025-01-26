from sqlalchemy import Column, Integer, String, Float, Date, MetaData, Table

# Define metadata
metadata = MetaData()

# Define the weather_data table
weather_data = Table(
    "weather_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("station_id", String, nullable=False),
    Column("date", Date, nullable=False),
    Column("max_temp", Float, nullable=True),  # Max temperature in Celsius
    Column("min_temp", Float, nullable=True),  # Min temperature in Celsius
    Column("precipitation", Float, nullable=True),  # Precipitation in cm
)

# Define the weather_stats table
weather_stats = Table(
    "weather_stats",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("station_id", String, nullable=False),
    Column("year", Integer, nullable=False),
    Column("avg_max_temp", Float, nullable=True),
    Column("avg_min_temp", Float, nullable=True),
    Column("total_precipitation", Float, nullable=True),
)

# Define the crop_yield_data table
crop_yield_data = Table(
    "crop_yield_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("year", Integer, nullable=False),
    Column("yield", Float, nullable=False),  # Crop yield in units (e.g., kg, tons, etc.)
)
