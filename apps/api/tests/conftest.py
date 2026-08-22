import pytest

@pytest.fixture
def app_settings():
    from app.core.config import settings
    return settings
