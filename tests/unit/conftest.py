import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def unit_test_setup():
    """
    Setup for unit tests.

    Unit tests should not require external services, so we only
    load environment variables for configuration if needed.
    """
    load_dotenv(".env", override=True)
    yield
