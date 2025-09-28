"""
Integration test configuration and fixtures.
"""
import pytest
import asyncio
import pathlib
import sys
from unittest.mock import patch, MagicMock
from asgi_lifespan import LifespanManager

# Add the project root directory to the Python path
project_root = str(pathlib.Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, project_root)

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def app_started(app_fixture):
    """Create a lifespan fixture for the FastAPI app with mocked scheduler."""
    # Mock the scheduler to prevent event loop issues
    with patch('app.main.scheduler') as mock_scheduler:
        mock_scheduler.add_job = MagicMock()
        mock_scheduler.start = MagicMock()
        mock_scheduler.shutdown = MagicMock()
        
        async with LifespanManager(app_fixture):
            yield app_fixture

@pytest.fixture(scope="session")
def app_fixture():
    """Get the FastAPI app from the system."""
    # Import the FastAPI app and models from the system
    from app.main import app
    return app

# Mark all tests in this directory as integration tests
pytestmark = pytest.mark.with_database