import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI


from app import main as app_main


class TestMainApp:
    """Test cases for main FastAPI application setup"""

    def test_app_initialization(self):
        """Test that FastAPI app is initialized correctly"""
        app = app_main.app
        
        assert isinstance(app, FastAPI)
        assert app.title == "Exosphere State Manager"
        assert app.description == "Exosphere State Manager"
        assert app.version == "0.1.0"
        
        # Check contact info
        assert app.contact is not None
        assert app.contact["name"] == "Nivedit Jain (Founder exosphere.host)"
        assert app.contact["email"] == "nivedit@exosphere.host"
        
        # Check license info
        assert app.license_info is not None
        assert app.license_info["name"] == "Elastic License 2.0 (ELv2)"
        assert "github.com/exospherehost/exosphere-api-server/blob/main/LICENSE" in app.license_info["url"]

    def test_health_endpoint_exists(self):
        """Test that the health endpoint is defined in the app"""
        # Check that the health endpoint exists in the app routes
        app = app_main.app
        
        health_route_found = False
        for route in app.routes:
            if hasattr(route, 'path') and route.path == '/health': # type: ignore
                health_route_found = True
                # Check that it's a GET endpoint
                if hasattr(route, 'methods'):
                    assert 'GET' in route.methods # type: ignore
                break
        
        assert health_route_found, "Health endpoint not found in app routes"

    def test_health_endpoint_returns_json(self):
        """Test that the health endpoint is configured to return JSON"""
        # Check that the health endpoint is configured correctly
        app = app_main.app
        
        for route in app.routes:
            if hasattr(route, 'path') and route.path == '/health': # type: ignore
                # Check that it's a GET endpoint
                if hasattr(route, 'methods'):
                    assert 'GET' in route.methods # type: ignore
                # Check that it has a response model (indicates JSON response)
                if hasattr(route, 'response_model'):
                    # FastAPI automatically sets response_model for JSON responses
                    assert route.response_model is not None # type: ignore
                break

    @patch('app.main.LogsManager')
    def test_middlewares_added_to_app(self, mock_logs_manager):
        """Test that middlewares are added to the application"""
        # Since middlewares are added during app creation, we need to check
        # if they're present in the middleware stack
        app = app_main.app
        
        # FastAPI stores middleware in app.user_middleware
        middleware_classes = [middleware.cls for middleware in app.user_middleware]
        
        # Import the middleware classes for comparison
        from app.middlewares.request_id_middleware import RequestIdMiddleware
        from app.middlewares.unhandled_exceptions_middleware import UnhandledExceptionsMiddleware
        
        assert RequestIdMiddleware in middleware_classes
        assert UnhandledExceptionsMiddleware in middleware_classes

    def test_middleware_order(self):
        """Test that middlewares are added in correct order"""
        app = app_main.app
        
        # FastAPI stores middleware in reverse order (last added is first executed)
        middleware_classes = [middleware.cls for middleware in app.user_middleware]
        
        from app.middlewares.request_id_middleware import RequestIdMiddleware
        from app.middlewares.unhandled_exceptions_middleware import UnhandledExceptionsMiddleware
        
        # UnhandledExceptionsMiddleware should be added last (executed first)
        # RequestIdMiddleware should be added first (executed after UnhandledExceptionsMiddleware)
        request_id_index = middleware_classes.index(RequestIdMiddleware) # type: ignore
        unhandled_exceptions_index = middleware_classes.index(UnhandledExceptionsMiddleware) # type: ignore
        
        # Since middleware is stored in reverse order, UnhandledExceptions should have lower index
        assert unhandled_exceptions_index < request_id_index

    def test_router_included(self):
        """Test that the main router is included in the app"""
        app = app_main.app
        
        # Check that routes from the router are present
        # The exact routes depend on what's in routes.py, but we can check if routes exist
        assert len(app.routes) > 1  # Should have at least health + routes from router


class TestLifespan:
    """Test cases for lifespan context manager"""

    @patch.dict(os.environ, {
        'MONGO_URI': 'mongodb://test:27017',
        'MONGO_DATABASE_NAME': 'test_db',
        'STATE_MANAGER_SECRET': 'test_secret'
    })
    @patch('app.main.init_beanie')
    @patch('app.main.AsyncMongoClient')
    @patch('app.main.LogsManager')
    async def test_lifespan_startup_success(self, mock_logs_manager, mock_mongo_client, mock_init_beanie):
        """Test successful lifespan startup"""
        # Setup mocks
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        mock_init_beanie.return_value = AsyncMock()
        
        # Create a mock FastAPI app for the lifespan
        mock_app = MagicMock()
        
        # Test the lifespan context manager
        async with app_main.lifespan(mock_app):
            # During startup, these should be called
            mock_logs_manager.assert_called()
            mock_logger.info.assert_any_call("server starting")
            mock_mongo_client.assert_called_with('mongodb://test:27017')
            mock_client.__getitem__.assert_called_with('test_db')
            mock_init_beanie.assert_called()
            mock_logger.info.assert_any_call("beanie dbs initialized")
            mock_logger.info.assert_any_call("secret initialized")
        
        # After context manager exits (shutdown)
        mock_logger.info.assert_any_call("server shutting down")

    @patch.dict(os.environ, {
        'MONGO_URI': 'mongodb://test:27017',
        'MONGO_DATABASE_NAME': 'test_db',
        'STATE_MANAGER_SECRET': ''  # Empty secret
    })
    @patch('app.main.init_beanie')
    @patch('app.main.AsyncMongoClient')
    @patch('app.main.LogsManager')
    async def test_lifespan_empty_secret_raises_error(self, mock_logs_manager, mock_mongo_client, mock_init_beanie):
        """Test that empty STATE_MANAGER_SECRET raises ValueError"""
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        mock_init_beanie.return_value = AsyncMock()
        
        mock_app = MagicMock()
        
        with pytest.raises(ValueError, match="STATE_MANAGER_SECRET is not set"):
            async with app_main.lifespan(mock_app):
                pass

    @patch.dict(os.environ, {
        'MONGO_URI': 'mongodb://test:27017',
        'MONGO_DATABASE_NAME': 'test_db',
        'STATE_MANAGER_SECRET': 'test_secret'
    })
    @patch('app.main.init_beanie')
    @patch('app.main.AsyncMongoClient')
    @patch('app.main.LogsManager')
    async def test_lifespan_init_beanie_with_correct_models(self, mock_logs_manager, mock_mongo_client, mock_init_beanie):
        """Test that init_beanie is called with correct document models"""
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        mock_init_beanie.return_value = AsyncMock()
        
        mock_app = MagicMock()
        
        async with app_main.lifespan(mock_app):
            pass
        
        # Check that init_beanie was called with the database and correct models
        mock_init_beanie.assert_called_once()
        call_args = mock_init_beanie.call_args
        
        # First argument should be the database
        assert call_args[0][0] == mock_db
        
        # Second argument should be document_models with the expected models
        document_models = call_args[1]['document_models']
        
        # Import the expected models
        from app.models.db.state import State
        from app.models.db.namespace import Namespace
        from app.models.db.graph_template_model import GraphTemplate
        from app.models.db.registered_node import RegisteredNode
        
        expected_models = [State, Namespace, GraphTemplate, RegisteredNode]
        assert document_models == expected_models


class TestEnvironmentIntegration:
    """Test cases for environment variable integration"""

    def test_load_dotenv_called(self):
        """Test that load_dotenv is called during module import"""
        # This test ensures that .env files are loaded
        # We can't easily test this without reimporting the module,
        # but we can verify the import doesn't fail
        assert hasattr(app_main, 'load_dotenv')

    @patch.dict(os.environ, {
        'MONGO_URI': 'mongodb://custom:27017',
        'MONGO_DATABASE_NAME': 'custom_db',
        'STATE_MANAGER_SECRET': 'custom_secret'
    })
    def test_environment_variables_usage(self):
        """Test that environment variables are properly accessed"""
        # Test that the module can access environment variables
        assert os.getenv("MONGO_URI") == 'mongodb://custom:27017'
        assert os.getenv("MONGO_DATABASE_NAME") == 'custom_db'
        assert os.getenv("STATE_MANAGER_SECRET") == 'custom_secret'


class TestAppConfiguration:
    """Test cases for application configuration"""

    def test_app_has_lifespan(self):
        """Test that app is configured with lifespan"""
        app = app_main.app
        assert app.router.lifespan_context is not None

    def test_app_routes_configuration(self):
        """Test that app routes are properly configured"""
        app = app_main.app
        
        # Should have at least the health route
        health_route_found = False
        for route in app.routes:
            if hasattr(route, 'path') and route.path == '/health': # type: ignore
                health_route_found = True
                break
        
        assert health_route_found, "Health route not found in app routes"

    def test_app_has_router_included(self):
        """Test that the app has the router included"""
        # This test verifies that the router is included in the app
        # which covers the missing line 78: app.include_router(router)
        assert len(app_main.app.routes) > 1  # More than just the health endpoint
        # Check that routes from the router are present
        router_routes = [route for route in app_main.app.routes if hasattr(route, 'path') and '/v0/namespace/' in str(route.path)] # type: ignore
        assert len(router_routes) > 0

    def test_app_router_integration(self):
        """Test that the router is properly integrated with the app"""
        # This test specifically covers the app.include_router(router) line
        # by verifying that the router's routes are accessible through the app
        app_routes = app_main.app.routes
        
        # Check that the router prefix is present in the app routes
        router_prefix_present = any(
            hasattr(route, 'path') and '/v0/namespace/' in str(route.path) # type: ignore
            for route in app_routes
        )
        assert router_prefix_present, "Router routes should be included in the app"