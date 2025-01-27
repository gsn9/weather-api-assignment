import time  # Added for tracking time
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
import logging
from app.etl.etl_interface import ETLInterface
from app.db.schema import WeatherData


class WeatherETL(ETLInterface):
    def __init__(self, session: AsyncSession, batch_size: int = 5000):
        """
        Initialize WeatherETL with the database session and batch size.

        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            batch_size (int, optional): Number of records per batch. Defaults to 5000.
        """
        self.session = session
        self.batch_size = batch_size

    def extract(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """
        Extract raw weather data from a tab-separated file.

        Args:
            file_content (bytes): Binary content of the uploaded file.
            filename (str): Name of the uploaded file.

        Returns:
            pd.DataFrame: Raw weather data.
        """
        logging.info(f"Extracting weather data from file: {filename}")
        buffer = pd.io.common.BytesIO(file_content)
        df = pd.read_csv(
            buffer,
            sep="\t",
            header=None,
            names=["date", "max_temp", "min_temp", "precipitation"],
            dtype={
                "date": str,
                "max_temp": float,
                "min_temp": float,
                "precipitation": float
            },
            na_values=-9999
        )
        df["station_id"] = filename.split(".")[0]  # Assuming station_id is the filename without extension
        logging.info(f"Extracted {len(df)} records from weather data.")
        return df

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw weather data by cleaning and removing duplicates.

        Args:
            data (pd.DataFrame): Raw weather data.

        Returns:
            pd.DataFrame: Cleaned weather data without duplicates.
        """
        logging.info("Transforming weather data.")
        # Convert 'date' column to datetime
        data["date"] = pd.to_datetime(data["date"], format="%Y%m%d", errors='coerce')

        # Scale temperature and precipitation values
        data["max_temp"] = data["max_temp"] / 10.0
        data["min_temp"] = data["min_temp"] / 10.0
        data["precipitation"] = data["precipitation"] / 10.0

        # Drop rows where all elements are NaN
        data.dropna(how="all", inplace=True)

        # Remove duplicate records based on 'station_id' and 'date'
        data.drop_duplicates(subset=["station_id", "date"], inplace=True)

        logging.info(f"Transformed weather data contains {len(data)} records after cleaning.")
        return data

    async def load(self, data: pd.DataFrame) -> int:
        """
        Load transformed weather data into the database using batch inserts with upsert.

        Args:
            data (pd.DataFrame): Transformed weather data.

        Returns:
            int: Total number of records successfully inserted.
        """
        logging.info("Loading weather data into the database.")
        rows_to_insert = data.to_dict(orient="records")
        total_inserted = 0
        total_rows = len(rows_to_insert)
        logging.info(f"Total rows to insert: {total_rows}")

        for start in range(0, total_rows, self.batch_size):
            end = start + self.batch_size
            batch = rows_to_insert[start:end]
            logging.info(f"Inserting rows {start + 1} to {min(end, total_rows)} into weather_data.")

            stmt = insert(WeatherData).values(batch)

            # Define the upsert behavior: do nothing on conflict
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['station_id', 'date']
            )

            try:
                result = await self.session.execute(stmt)
                # Use rowcount to track successful inserts
                total_inserted += result.rowcount or 0
                await self.session.commit()
                logging.info(f"Inserted rows {start + 1} to {min(end, total_rows)} successfully.")
            except Exception as e:
                await self.session.rollback()
                logging.error(f"Error inserting rows {start + 1} to {min(end, total_rows)}: {e}")
                raise e

        logging.info(f"Weather data loaded successfully. Total inserted: {total_inserted}.")
        return total_inserted

    async def run_etl(self, file_content: bytes, filename: str) -> dict:
        """
        Run the ETL process: extract, transform, and load weather data.

        Args:
            file_content (bytes): Binary content of the uploaded file.
            filename (str): Name of the uploaded file.

        Returns:
            dict: Summary of the ETL process, including total records, inserted records, and time taken.
        """
        start_time = time.time()  # Start tracking time

        # Extract
        raw_data = self.extract(file_content, filename)
        total_records = len(raw_data)

        # Transform
        transformed_data = self.transform(raw_data)

        # Load
        inserted_records = await self.load(transformed_data)

        # Calculate time taken
        end_time = time.time()
        time_taken = round(end_time - start_time, 2)

        # Return summary
        return {
            "total_records": total_records,
            "inserted_records": inserted_records,
            "time_taken": time_taken
        }
