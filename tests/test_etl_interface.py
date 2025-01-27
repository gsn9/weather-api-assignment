# tests/test_etl_interface.py
import pytest
import pandas as pd
from abc import ABC, abstractmethod
from unittest import mock
from app.etl.etl_interface import ETLInterface


def test_etl_interface_instantiation():
    with pytest.raises(TypeError) as exc_info:
        class ConcreteETL(ETLInterface):
            def extract(self, file_content: bytes, filename: str) -> pd.DataFrame:
                return pd.DataFrame()

            def transform(self, data: pd.DataFrame) -> pd.DataFrame:
                return data

            async def load(self, data):
                pass

        ConcreteETL()
    assert "Can't instantiate abstract class ETLInterface with abstract methods extract, load, transform" in str(exc_info.value)

def test_etl_interface_methods():
    class ConcreteETL(ETLInterface):
        def extract(self, file_content: bytes, filename: str) -> pd.DataFrame:
            return pd.DataFrame()

        def transform(self, data: pd.DataFrame) -> pd.DataFrame:
            return data

        async def load(self, data):
            pass

    etl = ConcreteETL()
    assert isinstance(etl, ETLInterface)
