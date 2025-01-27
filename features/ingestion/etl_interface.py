# etl_interface.py
from abc import ABC, abstractmethod
import pandas as pd

class ETLInterface(ABC):
    """
    Abstract base class for ETL processes.
    """

    @abstractmethod
    def extract(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """
        Extract raw data from the source.

        Args:
            file_content (bytes): Binary content of the uploaded file.
            filename (str): Name of the uploaded file.

        Returns:
            pd.DataFrame: Raw data.
        """
        pass

    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw data into a cleaned and structured format.

        Args:
            data (pd.DataFrame): Raw data.

        Returns:
            pd.DataFrame: Transformed data.
        """
        pass

    @abstractmethod
    async def load(self, data: pd.DataFrame):
        """
        Load transformed data into the target database.

        Args:
            data (pd.DataFrame): Transformed data.
        """
        pass

    async def run_etl(self, file_content: bytes, filename: str):
        """
        Execute the full ETL process: Extract, Transform, Load.

        Args:
            file_content (bytes): Binary content of the uploaded file.
            filename (str): Name of the uploaded file.
        """
        raw_data = self.extract(file_content, filename)
        transformed_data = self.transform(raw_data)
        await self.load(transformed_data)
