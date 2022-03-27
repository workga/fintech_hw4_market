import pytest

from app import create_app


@pytest.fixture(autouse=True)
def app():
    return create_app()
