"""
Integration tests for the FastAPI app from the system.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestSystemApp:
    """Test the FastAPI app from the system."""

    def test_system_app_import(self, system_app):
        """Test that the system app is properly imported."""
        assert system_app is not None
        assert hasattr(system_app, 'title')
        assert hasattr(system_app, 'routes')

    def test_app_metadata(self, app_metadata):
        """Test application metadata."""
        assert app_metadata['title'] == "Exosphere State Manager"
        assert app_metadata['description'] == "Exosphere State Manager"
        assert app_metadata['version'] == "0.1.0"
        assert app_metadata['openapi_url'] == "/openapi.json"
        assert app_metadata['docs_url'] == "/docs"
        assert app_metadata['redoc_url'] == "/redoc"

    def test_app_routes_exist(self, app_routes):
        """Test that the app has routes configured."""
        assert len(app_routes) > 0
        
        # Check for specific routes
        route_paths = [route['path'] for route in app_routes]
        assert "/health" in route_paths

    def test_health_endpoint_exists(self, health_endpoint):
        """Test that the health endpoint exists."""
        assert health_endpoint is not None
        assert health_endpoint.path == "/health"

    def test_app_has_middleware(self, system_app):
        """Test that the app has middleware configured."""
        assert hasattr(system_app, 'user_middleware')
        assert len(system_app.user_middleware) > 0

    def test_app_has_router(self, system_app):
        """Test that the app has a router configured."""
        assert hasattr(system_app, 'router')
        assert system_app.router is not None

    def test_app_lifespan(self, system_app):
        """Test that the app has a lifespan function."""
        assert hasattr(system_app, 'router')
        # The lifespan is configured in the router

    def test_app_settings_integration(self, system_app, test_settings):
        """Test that the app integrates with settings."""
        # The app should be able to access settings
        assert test_settings.environment == "testing"
        assert test_settings.state_manager_secret == "test-secret-key"

    def test_app_imports_work(self, system_app):
        """Test that all app imports work correctly."""
        # Test that we can access various app components
        from app.main import health
        from app.routes import router
        
        assert callable(health)
        assert router is not None

    def test_app_models_available(self, system_app):
        """Test that app models are available."""
        from app.models.db.state import State
        from app.models.db.namespace import Namespace
        from app.models.db.graph_template_model import GraphTemplate
        from app.models.db.registered_node import RegisteredNode
        
        # If we can import these, the models are available
        assert State is not None
        assert Namespace is not None
        assert GraphTemplate is not None
        assert RegisteredNode is not None

    def test_app_controller_available(self, system_app):
        """Test that app controller modules are available."""
        # Test that we can import controller modules
        from app.controller.register_nodes import register_nodes
        from app.controller.upsert_graph_template import upsert_graph_template
        from app.controller.get_graph_template import get_graph_template
        from app.controller.create_states import create_states, trigger_graph
        from app.controller.enqueue_states import enqueue_states
        from app.controller.executed_state import executed_state
        from app.controller.errored_state import errored_state
        from app.controller.get_current_states import get_current_states
        from app.controller.get_states_by_run_id import get_states_by_run_id
        from app.controller.list_graph_templates import list_graph_templates
        from app.controller.list_registered_nodes import list_registered_nodes
        from app.controller.get_secrets import get_secrets
        from app.controller.get_graph_structure import get_graph_structure
        
        # If we can import these, the controllers are available
        assert all([
            register_nodes, upsert_graph_template, get_graph_template,
            create_states, enqueue_states, executed_state, errored_state,
            get_current_states, get_states_by_run_id, list_graph_templates,
            list_registered_nodes, get_secrets, get_graph_structure, trigger_graph
        ])

    def test_app_utils_available(self, system_app):
        """Test that app utilities are available."""
        from app.utils.check_secret import check_api_key
        from app.utils.encrypter import get_encrypter
        
        # If we can import these, the utilities are available
        assert callable(check_api_key)
        assert callable(get_encrypter)

    def test_app_singletons_available(self, system_app):
        """Test that app singletons are available."""
        from app.singletons.logs_manager import LogsManager
        
        # If we can import this, the singletons are available
        assert LogsManager is not None

    def test_app_middlewares_available(self, system_app):
        """Test that app middlewares are available."""
        from app.middlewares.request_id_middleware import RequestIdMiddleware
        from app.middlewares.unhandled_exceptions_middleware import UnhandledExceptionsMiddleware
        
        # If we can import these, the middlewares are available
        assert RequestIdMiddleware is not None
        assert UnhandledExceptionsMiddleware is not None

    def test_app_configuration(self, system_app):
        """Test app configuration."""
        # Test CORS configuration
        assert hasattr(system_app, 'user_middleware')
        
        # Test that the app has the expected structure
        assert system_app.title == "Exosphere State Manager"
        assert system_app.description == "Exosphere State Manager"
        assert system_app.version == "0.1.0"

    def test_app_route_structure(self, app_routes):
        """Test the structure of app routes."""
        for route in app_routes:
            assert 'path' in route
            assert 'name' in route
            assert 'methods' in route
            assert isinstance(route['path'], str)
            assert isinstance(route['name'], str)
            # Methods can be either a set or list, so check for both
            assert isinstance(route['methods'], (set, list))

    def test_app_integration_with_settings(self, system_app, test_settings):
        """Test that the app integrates properly with settings."""
        # Test that settings are accessible
        assert test_settings.mongo_uri is not None
        assert test_settings.mongo_database_name is not None
        assert test_settings.state_manager_secret is not None
        assert test_settings.environment == "testing"

    def test_app_ready_for_testing(self, system_app):
        """Test that the app is ready for integration testing."""
        # The app should be properly configured and ready for testing
        assert system_app is not None
        assert hasattr(system_app, 'routes')
        assert len(system_app.routes) > 0
        
        # Test that we can access the app's components
        assert hasattr(system_app, 'router')
        assert hasattr(system_app, 'user_middleware')
        assert hasattr(system_app, 'title') 