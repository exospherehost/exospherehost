"""
Integration test configuration and fixtures.
"""
import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch
import sys
from pathlib import Path

# Add the project root to Python path to ensure proper imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app and models from the system
from app.main import app
from app.config.settings import get_settings, Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Get test settings with test configuration."""
    # Override settings for testing
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["STATE_MANAGER_SECRET"] = "test-secret-key"
    
    return get_settings()


@pytest.fixture(scope="session")
def system_app():
    """Get the FastAPI app from the system."""
    return app


@pytest.fixture(scope="session")
async def test_app(test_settings: Settings):
    """Create a test FastAPI app with mocked database."""
    # Mock the database initialization to avoid requiring MongoDB
    with patch('app.main.init_beanie') as mock_init_beanie:
        mock_init_beanie.return_value = AsyncMock()
        yield app


@pytest.fixture
def test_api_key(test_settings: Settings) -> str:
    """Get the test API key."""
    return test_settings.state_manager_secret


@pytest.fixture
def test_namespace() -> str:
    """Generate a unique test namespace."""
    import uuid
    return f"test-namespace-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_graph_name() -> str:
    """Generate a unique test graph name."""
    import uuid
    return f"test-graph-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_runtime_name() -> str:
    """Generate a unique test runtime name."""
    import uuid
    return f"test-runtime-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_node_registration():
    """Create a sample node registration for testing."""
    from app.models.register_nodes_request import NodeRegistrationModel
    
    return NodeRegistrationModel(
        name="TestNode",
        inputs_schema={
            "type": "object",
            "properties": {
                "input1": {"type": "string"},
                "input2": {"type": "number"}
            },
            "required": ["input1", "input2"]
        },
        outputs_schema={
            "type": "object",
            "properties": {
                "output1": {"type": "string"},
                "output2": {"type": "number"}
            }
        },
        secrets=["test_secret"]
    )


@pytest.fixture
def sample_graph_nodes(test_namespace: str):
    """Create sample graph nodes for testing."""
    from app.models.graph_models import NodeTemplate
    
    return [
        NodeTemplate(
            node_name="TestNode",
            namespace=test_namespace,
            identifier="node1",
            inputs={
                "input1": "test_value",
                "input2": 42
            },
            next_nodes=["node2"]
        ),
        NodeTemplate(
            node_name="TestNode",
            namespace=test_namespace,
            identifier="node2",
            inputs={
                "input1": "{{node1.output1}}",
                "input2": "{{node1.output2}}"
            },
            next_nodes=[]
        )
    ]


@pytest.fixture
def app_routes(system_app):
    """Get all available routes from the system app."""
    routes = []
    for route in system_app.routes:
        if hasattr(route, 'path'):
            routes.append({
                'path': route.path,
                'name': route.name,
                'methods': getattr(route, 'methods', [])
            })
    return routes


@pytest.fixture
def app_metadata(system_app):
    """Get application metadata from the system app."""
    return {
        'title': system_app.title,
        'description': system_app.description,
        'version': system_app.version,
        'openapi_url': system_app.openapi_url,
        'docs_url': system_app.docs_url,
        'redoc_url': system_app.redoc_url
    }


@pytest.fixture
def health_endpoint(system_app):
    """Get the health endpoint from the system app."""
    # Find the health endpoint
    for route in system_app.routes:
        if hasattr(route, 'path') and route.path == "/health":
            return route
    return None


# Mark all tests in this directory as integration tests
pytestmark = pytest.mark.integration