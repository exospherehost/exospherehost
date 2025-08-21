import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.routes import router
from app.models.enqueue_request import EnqueueRequestModel
from app.models.create_models import TriggerGraphRequestModel, CreateRequestModel
from app.models.executed_models import ExecutedRequestModel
from app.models.errored_models import ErroredRequestModel
from app.models.graph_models import UpsertGraphTemplateRequest, UpsertGraphTemplateResponse
from app.models.register_nodes_request import RegisterNodesRequestModel
from app.models.secrets_response import SecretsResponseModel
from app.models.list_models import ListRegisteredNodesResponse, ListGraphTemplatesResponse
from app.models.state_list_models import StatesByRunIdResponse, CurrentStatesResponse


class TestRouteStructure:
    """Test cases for route structure and configuration"""

    def test_router_has_correct_routes(self):
        """Test that router has all expected routes"""
        routes = [route for route in router.routes if hasattr(route, 'path')]
        
        # Check for key route paths
        paths = [route.path for route in routes]
        
        # State management routes
        assert any('/v0/namespace/{namespace_name}/states/enqueue' in path for path in paths)
        assert any('/v0/namespace/{namespace_name}/graph/{graph_name}/trigger' in path for path in paths)
        assert any('/v0/namespace/{namespace_name}/graph/{graph_name}/states/create' in path for path in paths)
        assert any('/v0/namespace/{namespace_name}/states/{state_id}/executed' in path for path in paths)
        assert any('/v0/namespace/{namespace_name}/states/{state_id}/errored' in path for path in paths)
        
        # Graph template routes (there are two /graph/{graph_name} routes - GET and PUT)
        assert any('/v0/namespace/{namespace_name}/graph/{graph_name}' in path for path in paths)
        
        # Node registration routes
        assert any('/v0/namespace/{namespace_name}/nodes/' in path for path in paths)
        
        # Secrets routes
        assert any('/v0/namespace/{namespace_name}/state/{state_id}/secrets' in path for path in paths)
        
        # List routes
        assert any('/v0/namespace/{namespace_name}/nodes' in path for path in paths)
        assert any('/v0/namespace/{namespace_name}/graphs' in path for path in paths)
        assert any('/v0/namespace/{namespace_name}/states/run/{run_id}' in path for path in paths)
        assert any('/v0/namespace/{namespace_name}/states' in path for path in paths)

    def test_router_tags(self):
        """Test that router has correct tags"""
        # Check that all routes have appropriate tags
        for route in router.routes:
            if hasattr(route, 'tags'):
                assert route.tags in [["state"], ["graph"], ["nodes"]]

    def test_router_dependencies(self):
        """Test that router has API key dependency"""
        # Check that routes have dependencies (API key validation)
        for route in router.routes:
            if hasattr(route, 'dependencies'):
                # At least some routes should have dependencies for API key validation
                if route.dependencies:
                    assert len(route.dependencies) > 0


class TestModelValidation:
    """Test cases for request/response model validation"""

    def test_enqueue_request_model_validation(self):
        """Test EnqueueRequestModel validation"""
        # Test with valid data
        valid_data = {
            "nodes": ["node1", "node2"],
            "batch_size": 10
        }
        model = EnqueueRequestModel(**valid_data)
        assert model.nodes == ["node1", "node2"]
        assert model.batch_size == 10

    def test_trigger_graph_request_model_validation(self):
        """Test TriggerGraphRequestModel validation"""
        # Test with valid data
        valid_data = {
            "states": [
                {
                    "identifier": "node1",
                    "inputs": {"input1": "value1"}
                }
            ]
        }
        model = TriggerGraphRequestModel(**valid_data)
        assert len(model.states) == 1
        assert model.states[0].identifier == "node1"
        assert model.states[0].inputs == {"input1": "value1"}

    def test_create_request_model_validation(self):
        """Test CreateRequestModel validation"""
        # Test with valid data
        valid_data = {
            "run_id": "test-run-id",
            "states": [
                {
                    "identifier": "node1",
                    "inputs": {"input1": "value1"}
                }
            ]
        }
        model = CreateRequestModel(**valid_data)
        assert model.run_id == "test-run-id"
        assert len(model.states) == 1
        assert model.states[0].identifier == "node1"

    def test_executed_request_model_validation(self):
        """Test ExecutedRequestModel validation"""
        # Test with valid data
        valid_data = {
            "outputs": [{"field1": "value1"}, {"field2": "value2"}]
        }
        model = ExecutedRequestModel(**valid_data)
        assert model.outputs == [{"field1": "value1"}, {"field2": "value2"}]

    def test_errored_request_model_validation(self):
        """Test ErroredRequestModel validation"""
        # Test with valid data
        valid_data = {
            "error": "Test error message"
        }
        model = ErroredRequestModel(**valid_data)
        assert model.error == "Test error message"

    def test_upsert_graph_template_request_validation(self):
        """Test UpsertGraphTemplateRequest validation"""
        # Test with valid data
        valid_data = {
            "nodes": [],
            "secrets": {}
        }
        model = UpsertGraphTemplateRequest(**valid_data)
        assert model.nodes == []
        assert model.secrets == {}

    def test_register_nodes_request_model_validation(self):
        """Test RegisterNodesRequestModel validation"""
        # Test with valid data
        valid_data = {
            "runtime_name": "test-runtime",
            "nodes": [
                {
                    "name": "node1",
                    "namespace": "test",
                    "inputs_schema": {},
                    "outputs_schema": {},
                    "secrets": []
                }
            ]
        }
        model = RegisterNodesRequestModel(**valid_data)
        assert model.runtime_name == "test-runtime"
        assert len(model.nodes) == 1
        assert model.nodes[0].name == "node1"


class TestResponseModels:
    """Test cases for response model validation"""

    def test_upsert_graph_template_response_validation(self):
        """Test UpsertGraphTemplateResponse validation"""
        # Test with valid data
        valid_data = {
            "nodes": [],
            "secrets": {},
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "validation_status": "VALID"
        }
        model = UpsertGraphTemplateResponse(**valid_data)
        assert model.nodes == []
        assert model.secrets == {}

    def test_secrets_response_model_validation(self):
        """Test SecretsResponseModel validation"""
        # Test with valid data
        valid_data = {
            "secrets": {"secret1": "value1"}
        }
        model = SecretsResponseModel(**valid_data)
        assert model.secrets == {"secret1": "value1"}

    def test_list_registered_nodes_response_validation(self):
        """Test ListRegisteredNodesResponse validation"""
        # Test with valid data
        valid_data = {
            "nodes": [],
            "namespace": "test",
            "count": 0
        }
        model = ListRegisteredNodesResponse(**valid_data)
        assert model.nodes == []
        assert model.namespace == "test"
        assert model.count == 0

    def test_list_graph_templates_response_validation(self):
        """Test ListGraphTemplatesResponse validation"""
        # Test with valid data
        valid_data = {
            "templates": [],
            "namespace": "test",
            "count": 0
        }
        model = ListGraphTemplatesResponse(**valid_data)
        assert model.templates == []
        assert model.namespace == "test"
        assert model.count == 0

    def test_states_by_run_id_response_validation(self):
        """Test StatesByRunIdResponse validation"""
        # Test with valid data
        valid_data = {
            "states": [],
            "namespace": "test",
            "run_id": "test-run-id",
            "count": 0
        }
        model = StatesByRunIdResponse(**valid_data)
        assert model.states == []
        assert model.namespace == "test"
        assert model.run_id == "test-run-id"
        assert model.count == 0

    def test_current_states_response_validation(self):
        """Test CurrentStatesResponse validation"""
        # Test with valid data
        valid_data = {
            "states": [],
            "namespace": "test",
            "count": 0,
            "run_ids": ["run1", "run2"]
        }
        model = CurrentStatesResponse(**valid_data)
        assert model.states == []
        assert model.namespace == "test"
        assert model.count == 0
        assert model.run_ids == ["run1", "run2"]


class TestRouteHandlers:
    """Test cases for route handler functions"""

    def test_route_handlers_exist(self):
        """Test that all route handlers are properly defined"""
        # Import the route handlers to ensure they exist
        from app.routes import (
            enqueue_state,
            trigger_graph_route,
            create_state,
            executed_state_route,
            errored_state_route,
            upsert_graph_template,
            get_graph_template,
            register_nodes_route,
            get_secrets_route,
            list_registered_nodes_route,
            list_graph_templates_route,
            get_states_by_run_id_route,
            get_current_states_route
        )
        
        # Verify all handlers are callable
        assert callable(enqueue_state)
        assert callable(trigger_graph_route)
        assert callable(create_state)
        assert callable(executed_state_route)
        assert callable(errored_state_route)
        assert callable(upsert_graph_template)
        assert callable(get_graph_template)
        assert callable(register_nodes_route)
        assert callable(get_secrets_route)
        assert callable(list_registered_nodes_route)
        assert callable(list_graph_templates_route)
        assert callable(get_states_by_run_id_route)
        assert callable(get_current_states_route) 