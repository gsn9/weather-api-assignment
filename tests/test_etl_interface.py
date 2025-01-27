# tests/test_etl_interface.py

import pytest
from app.etl.etl_interface import ETLInterface


def test_etl_interface_abstract_methods():
    """
    Test that ETLInterface cannot be instantiated directly and requires all abstract methods to be implemented.
    """
    with pytest.raises(TypeError):
        ETLInterface()


def test_etl_interface_requires_methods():
    """
    Test that any subclass of ETLInterface must implement the abstract methods.
    """

    class IncompleteETL(ETLInterface):
        def extract(self, file_content: bytes, filename: str):
            pass  # Implement only one method

    with pytest.raises(TypeError):
        IncompleteETL()
