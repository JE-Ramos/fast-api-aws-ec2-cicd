import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.config import Settings, get_settings


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_settings():
    test_settings = Settings(
        app_name="Test App",
        environment="testing",
        debug=False,
        aws_region="us-test-1"
    )
    return test_settings


@pytest.fixture
def override_settings(mock_settings):
    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def sample_item():
    return {
        "id": 1,
        "name": "Sample Item",
        "description": "A sample test item"
    }


@pytest.fixture
def sample_items_list():
    return [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
        {"id": 3, "name": "Item 3"}
    ]