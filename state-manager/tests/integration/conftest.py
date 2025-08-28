"""
Integration test configuration and fixtures.
"""
import os
import pytest
import asyncio
from typing import Generator
from unittest.mock import AsyncMock, patch
import sys
from pathlib import Path

# Add the project root to Python path to ensure proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app and models from the system
from app.main import app

@pytest.fixture(scope="session")
def app_fixture():
    """Get the FastAPI app from the system."""
    return app

# Mark all tests in this directory as integration tests
pytestmark = pytest.mark.integration