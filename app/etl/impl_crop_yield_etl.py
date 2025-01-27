import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
import logging
from app.etl.etl_interface import ETLInterface
from app.db.schema import CropYieldData
import time


class CropYieldETL(ETLInterface):
    def __init__(self, session: AsyncSession, batch_size: int = 5000):
        """
        Initialize CropYieldETL with the database session and batch size.

        Args:
            session (AsyncSession): SQLAlchemy asynchronous session.
            batch_size (int, optional): Number of records per batch. Defaults to 5000.
        """
        self.session = session
        self.batch_size = batch_size

    def extract(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """
        Extract raw crop yield data from a tab-separated CSV file.

        Args:
            file_content (bytes): Binary content of the uploaded file.
            filename (str): Name of the uploaded file.

        Returns:
            pd.DataFrame: Raw crop yield data.
        """
        logging.info(f"Extracting crop yield data from file: {filename}")
        buffer = pd.io.common.BytesIO(file_content)
        df = pd.read_csv(
            buffer,
            sep="\t",  # Tab-separated values
            header=None,  # No headers in the file
            names=["year", "yield_value"],  # Correct column names
            dtype={"year": float, "yield_value": float},
            na_values=-9999,  # Replace sentinel values with NaN
        )
        station_id = filename.split(".")[0]
        df["station_id"] = station_id
        logging.info(f"Extracted {len(df)} records from crop yield data.")
        return df

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw crop yield data by cleaning and removing duplicates.

        Args:
            data (pd.DataFrame): Raw crop yield data.

        Returns:
            pd.DataFrame: Cleaned crop yield data without duplicates.
        """
        logging.info("Transforming crop yield data.")
        # Ensure correct data types
        data["year"] = pd.to_numeric(data["year"], errors="coerce").astype("int64")
        data["yield_value"] = pd.to_numeric(
            data["yield_value"], errors="coerce"
        ).astype("float64")

        # Drop rows with all NaN values
        data.dropna(how="all", inplace=True)

        # Remove duplicate records based on 'station_id' and 'year'
        data.drop_duplicates(subset=["station_id", "year"], inplace=True)

        logging.info(
            f"Transformed crop yield data contains {len(data)} records after cleaning."
        )
        return data

    async def load(self, data: pd.DataFrame) -> int:
        """
        Load transformed crop yield data into the database using batch inserts with upsert.

        Args:
            data (pd.DataFrame): Transformed crop yield data.

        Returns:
            int: The number of rows successfully inserted.
        """
        logging.info("Loading crop yield data into the database.")
        rows_to_insert = data.to_dict(orient="records")
        total_rows = len(rows_to_insert)
        inserted_rows = 0
        logging.info(f"Total crop yield rows to insert: {total_rows}")

        for start in range(0, total_rows, self.batch_size):
            end = start + self.batch_size
            batch = rows_to_insert[start:end]
            logging.info(
                f"Inserting crop yield rows {start + 1} to {min(end, total_rows)} into crop_yield_data."
            )

            stmt = insert(CropYieldData).values(batch)

            # Define the upsert behavior: do nothing on conflict
            stmt = stmt.on_conflict_do_nothing(index_elements=["station_id", "year"])

            try:
                result = await self.session.execute(stmt)
                await self.session.commit()
                inserted_rows += result.rowcount or len(batch)
                logging.info(
                    f"Inserted crop yield rows {start + 1} to {min(end, total_rows)} successfully."
                )
            except Exception as e:
                await self.session.rollback()
                logging.error(
                    f"Error inserting crop yield rows {start + 1} to {min(end, total_rows)}: {e}"
                )
                raise e

        logging.info("Crop yield data loaded successfully.")
        return inserted_rows

    async def run_etl(self, file_content: bytes, filename: str) -> dict:
        """
        Run the ETL process: Extract, Transform, and Load.

        Args:
            file_content (bytes): Binary content of the uploaded file.
            filename (str): Name of the uploaded file.

        Returns:
            dict: Feedback about the ETL process (e.g., total records, inserted records, time taken).
        """
        start_time = time.time()

        # Extract
        raw_data = self.extract(file_content, filename)

        # Transform
        transformed_data = self.transform(raw_data)

        # Load
        inserted_rows = await self.load(transformed_data)

        # Calculate total time taken
        total_time = time.time() - start_time

        feedback = {
            "total_records": len(raw_data),
            "inserted_records": inserted_rows,
            "time_taken": round(total_time, 2),  # Round to 2 decimal places
        }
        logging.info(f"ETL process completed: {feedback}")
        return feedback
