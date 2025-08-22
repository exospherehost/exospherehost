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

import pytest
from unittest.mock import MagicMock, patch


class TestRouteStructure:
    """Test cases for route structure and configuration"""

    def test_router_has_correct_routes(self):
        """Test that router has all expected routes"""
        routes = [route for route in router.routes if hasattr(route, 'path')]
        
        # Check for key route paths
        paths = [route.path for route in routes] # type: ignore
        
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
                assert route.tags in [["state"], ["graph"], ["nodes"]] # type: ignore

    def test_router_dependencies(self):
        """Test that router has API key dependency"""
        # Check that routes have dependencies (API key validation)
        for route in router.routes:
            if hasattr(route, 'dependencies'):
                # At least some routes should have dependencies for API key validation
                if route.dependencies: # type: ignore
                    assert len(route.dependencies) > 0 # type: ignore


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
        model = TriggerGraphRequestModel(**valid_data) # type: ignore
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


class TestRouteHandlerAPIKeyValidation:
    """Test cases for API key validation in route handlers"""

    @pytest.fixture
    def mock_request(self):
        """Mock request object with request_id"""
        request = MagicMock()
        request.state.x_exosphere_request_id = "test-request-id"
        return request

    @pytest.fixture
    def mock_request_no_id(self):
        """Mock request object without request_id"""
        request = MagicMock()
        delattr(request.state, 'x_exosphere_request_id')
        return request

    @pytest.fixture
    def mock_background_tasks(self):
        """Mock background tasks"""
        return MagicMock()

    @patch('app.routes.enqueue_states')
    async def test_enqueue_state_with_valid_api_key(self, mock_enqueue_states, mock_request):
        """Test enqueue_state with valid API key"""
        from app.routes import enqueue_state
        from app.models.enqueue_request import EnqueueRequestModel
        
        # Arrange
        mock_enqueue_states.return_value = MagicMock()
        body = EnqueueRequestModel(nodes=["node1"], batch_size=1)
        
        # Act
        result = await enqueue_state("test_namespace", body, mock_request, "valid_key")
        
        # Assert
        mock_enqueue_states.assert_called_once_with("test_namespace", body, "test-request-id")
        assert result == mock_enqueue_states.return_value

    @patch('app.routes.enqueue_states')
    async def test_enqueue_state_with_invalid_api_key(self, mock_enqueue_states, mock_request):
        """Test enqueue_state with invalid API key"""
        from app.routes import enqueue_state
        from app.models.enqueue_request import EnqueueRequestModel
        from fastapi import HTTPException
        
        # Arrange
        body = EnqueueRequestModel(nodes=["node1"], batch_size=1)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await enqueue_state("test_namespace", body, mock_request, None)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid API key"

    @patch('app.routes.enqueue_states')
    async def test_enqueue_state_without_request_id(self, mock_enqueue_states, mock_request_no_id):
        """Test enqueue_state without request_id in request state"""
        from app.routes import enqueue_state
        from app.models.enqueue_request import EnqueueRequestModel
        from unittest.mock import patch
        
        # Arrange
        mock_enqueue_states.return_value = MagicMock()
        body = EnqueueRequestModel(nodes=["node1"], batch_size=1)
        
        # Act
        with patch('app.routes.uuid4') as mock_uuid:
            mock_uuid.return_value = "generated-request-id"
            result = await enqueue_state("test_namespace", body, mock_request_no_id, "valid_key")
        
        # Assert
        mock_enqueue_states.assert_called_once_with("test_namespace", body, "generated-request-id")
        assert result == mock_enqueue_states.return_value

    @patch('app.routes.trigger_graph')
    async def test_trigger_graph_route_with_valid_api_key(self, mock_trigger_graph, mock_request):
        """Test trigger_graph_route with valid API key"""
        from app.routes import trigger_graph_route
        from app.models.create_models import TriggerGraphRequestModel
        
        # Arrange
        mock_trigger_graph.return_value = MagicMock()
        body = TriggerGraphRequestModel(states=[])
        
        # Act
        result = await trigger_graph_route("test_namespace", "test_graph", body, mock_request, "valid_key")
        
        # Assert
        mock_trigger_graph.assert_called_once_with("test_namespace", "test_graph", body, "test-request-id")
        assert result == mock_trigger_graph.return_value

    @patch('app.routes.trigger_graph')
    async def test_trigger_graph_route_with_invalid_api_key(self, mock_trigger_graph, mock_request):
        """Test trigger_graph_route with invalid API key"""
        from app.routes import trigger_graph_route
        from app.models.create_models import TriggerGraphRequestModel
        from fastapi import HTTPException
        
        # Arrange
        body = TriggerGraphRequestModel(states=[])
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await trigger_graph_route("test_namespace", "test_graph", body, mock_request, None)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid API key"

    @patch('app.routes.create_states')
    async def test_create_state_with_valid_api_key(self, mock_create_states, mock_request):
        """Test create_state with valid API key"""
        from app.routes import create_state
        from app.models.create_models import CreateRequestModel
        
        # Arrange
        mock_create_states.return_value = MagicMock()
        body = CreateRequestModel(run_id="test_run", states=[])
        
        # Act
        result = await create_state("test_namespace", "test_graph", body, mock_request, "valid_key")
        
        # Assert
        mock_create_states.assert_called_once_with("test_namespace", "test_graph", body, "test-request-id")
        assert result == mock_create_states.return_value

    @patch('app.routes.executed_state')
    async def test_executed_state_route_with_valid_api_key(self, mock_executed_state, mock_request, mock_background_tasks):
        """Test executed_state_route with valid API key"""
        from app.routes import executed_state_route
        from app.models.executed_models import ExecutedRequestModel
        
        # Arrange
        mock_executed_state.return_value = MagicMock()
        body = ExecutedRequestModel(outputs=[])
        
        # Act
        result = await executed_state_route("test_namespace", "507f1f77bcf86cd799439011", body, mock_request, mock_background_tasks, "valid_key")
        
        # Assert
        mock_executed_state.assert_called_once()
        assert result == mock_executed_state.return_value

    @patch('app.routes.errored_state')
    async def test_errored_state_route_with_valid_api_key(self, mock_errored_state, mock_request):
        """Test errored_state_route with valid API key"""
        from app.routes import errored_state_route
        from app.models.errored_models import ErroredRequestModel
        
        # Arrange
        mock_errored_state.return_value = MagicMock()
        body = ErroredRequestModel(error="test error")
        
        # Act
        result = await errored_state_route("test_namespace", "507f1f77bcf86cd799439011", body, mock_request, "valid_key")
        
        # Assert
        mock_errored_state.assert_called_once()
        assert result == mock_errored_state.return_value

    @patch('app.routes.upsert_graph_template_controller')
    async def test_upsert_graph_template_with_valid_api_key(self, mock_upsert, mock_request, mock_background_tasks):
        """Test upsert_graph_template with valid API key"""
        from app.routes import upsert_graph_template
        from app.models.graph_models import UpsertGraphTemplateRequest
        
        # Arrange
        mock_upsert.return_value = MagicMock()
        body = UpsertGraphTemplateRequest(nodes=[], secrets={})
        
        # Act
        result = await upsert_graph_template("test_namespace", "test_graph", body, mock_request, mock_background_tasks, "valid_key")
        
        # Assert
        mock_upsert.assert_called_once_with("test_namespace", "test_graph", body, "test-request-id", mock_background_tasks)
        assert result == mock_upsert.return_value

    @patch('app.routes.get_graph_template_controller')
    async def test_get_graph_template_with_valid_api_key(self, mock_get, mock_request):
        """Test get_graph_template with valid API key"""
        from app.routes import get_graph_template
        
        # Arrange
        mock_get.return_value = MagicMock()
        
        # Act
        result = await get_graph_template("test_namespace", "test_graph", mock_request, "valid_key")
        
        # Assert
        mock_get.assert_called_once_with("test_namespace", "test_graph", "test-request-id")
        assert result == mock_get.return_value

    @patch('app.routes.register_nodes')
    async def test_register_nodes_route_with_valid_api_key(self, mock_register, mock_request):
        """Test register_nodes_route with valid API key"""
        from app.routes import register_nodes_route
        from app.models.register_nodes_request import RegisterNodesRequestModel
        
        # Arrange
        mock_register.return_value = MagicMock()
        body = RegisterNodesRequestModel(runtime_name="test_runtime", nodes=[])
        
        # Act
        result = await register_nodes_route("test_namespace", body, mock_request, "valid_key")
        
        # Assert
        mock_register.assert_called_once_with("test_namespace", body, "test-request-id")
        assert result == mock_register.return_value

    @patch('app.routes.get_secrets')
    async def test_get_secrets_route_with_valid_api_key(self, mock_get_secrets, mock_request):
        """Test get_secrets_route with valid API key"""
        from app.routes import get_secrets_route
        
        # Arrange
        mock_get_secrets.return_value = MagicMock()
        
        # Act
        result = await get_secrets_route("test_namespace", "test_state_id", mock_request, "valid_key")
        
        # Assert
        mock_get_secrets.assert_called_once_with("test_namespace", "test_state_id", "test-request-id")
        assert result == mock_get_secrets.return_value

    @patch('app.routes.list_registered_nodes')
    async def test_list_registered_nodes_route_with_valid_api_key(self, mock_list_nodes, mock_request):
        """Test list_registered_nodes_route with valid API key"""
        from app.routes import list_registered_nodes_route
        
        # Arrange
        mock_list_nodes.return_value = []
        
        # Act
        result = await list_registered_nodes_route("test_namespace", mock_request, "valid_key")
        
        # Assert
        mock_list_nodes.assert_called_once_with("test_namespace", "test-request-id")
        assert result.namespace == "test_namespace"
        assert result.count == 0
        assert result.nodes == []

    @patch('app.routes.list_graph_templates')
    async def test_list_graph_templates_route_with_valid_api_key(self, mock_list_templates, mock_request):
        """Test list_graph_templates_route with valid API key"""
        from app.routes import list_graph_templates_route
        
        # Arrange
        mock_list_templates.return_value = []
        
        # Act
        result = await list_graph_templates_route("test_namespace", mock_request, "valid_key")
        
        # Assert
        mock_list_templates.assert_called_once_with("test_namespace", "test-request-id")
        assert result.namespace == "test_namespace"
        assert result.count == 0
        assert result.templates == []

    @patch('app.routes.get_current_states')
    async def test_get_current_states_route_with_valid_api_key(self, mock_get_states, mock_request):
        """Test get_current_states_route with valid API key"""
        from app.routes import get_current_states_route
        from app.models.db.state import State
        from beanie import PydanticObjectId
        from datetime import datetime
        
        # Arrange
        mock_state = MagicMock(spec=State)
        mock_state.id = PydanticObjectId()
        mock_state.node_name = "test_node"
        mock_state.identifier = "test_identifier"
        mock_state.namespace_name = "test_namespace"
        mock_state.graph_name = "test_graph"
        mock_state.run_id = "test_run"
        mock_state.status = "CREATED"
        mock_state.inputs = {"key": "value"}
        mock_state.outputs = {"output": "result"}
        mock_state.error = None
        mock_state.parents = {"parent1": PydanticObjectId()}
        mock_state.created_at = datetime.now()
        mock_state.updated_at = datetime.now()
        
        mock_get_states.return_value = [mock_state]
        
        # Act
        result = await get_current_states_route("test_namespace", mock_request, "valid_key")
        
        # Assert
        mock_get_states.assert_called_once_with("test_namespace", "test-request-id")
        assert result.namespace == "test_namespace"
        assert result.count == 1
        assert len(result.states) == 1
        assert result.run_ids == ["test_run"]

    @patch('app.routes.get_states_by_run_id')
    async def test_get_states_by_run_id_route_with_valid_api_key(self, mock_get_states, mock_request):
        """Test get_states_by_run_id_route with valid API key"""
        from app.routes import get_states_by_run_id_route
        from app.models.db.state import State
        from beanie import PydanticObjectId
        from datetime import datetime
        
        # Arrange
        mock_state = MagicMock(spec=State)
        mock_state.id = PydanticObjectId()
        mock_state.node_name = "test_node"
        mock_state.identifier = "test_identifier"
        mock_state.namespace_name = "test_namespace"
        mock_state.graph_name = "test_graph"
        mock_state.run_id = "test_run"
        mock_state.status = "CREATED"
        mock_state.inputs = {"key": "value"}
        mock_state.outputs = {"output": "result"}
        mock_state.error = None
        mock_state.parents = {"parent1": PydanticObjectId()}
        mock_state.created_at = datetime.now()
        mock_state.updated_at = datetime.now()
        
        mock_get_states.return_value = [mock_state]
        
        # Act
        result = await get_states_by_run_id_route("test_namespace", "test_run", mock_request, "valid_key")
        
        # Assert
        mock_get_states.assert_called_once_with("test_namespace", "test_run", "test-request-id")
        assert result.namespace == "test_namespace"
        assert result.run_id == "test_run"
        assert result.count == 1
        assert len(result.states) == 1 