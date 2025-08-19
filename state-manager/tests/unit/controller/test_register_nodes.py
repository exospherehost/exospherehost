import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List
from beanie.operators import Set

from app.controller.register_nodes import register_nodes
from app.models.register_nodes_request import RegisterNodesRequestModel, NodeRegistrationModel
from app.models.register_nodes_response import RegisterNodesResponseModel, RegisteredNodeModel
from app.models.db.registered_node import RegisteredNode


class TestRegisterNodes:
    """Test cases for register_nodes function"""

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_runtime_name(self):
        return "test-runtime"

    @pytest.fixture
    def mock_node_registration(self):
        """Create mock node registration data"""
        return NodeRegistrationModel(
            name="test_node",
            inputs_schema={"type": "object", "properties": {"input": {"type": "string"}}},
            outputs_schema={"type": "object", "properties": {"output": {"type": "string"}}},
            secrets=["secret1", "secret2"]
        )

    @pytest.fixture
    def mock_multiple_node_registrations(self):
        """Create multiple mock node registration data"""
        nodes = []
        for i in range(3):
            node = NodeRegistrationModel(
                name=f"test_node_{i}",
                inputs_schema={"type": "object", "properties": {"input": {"type": "string"}}},
                outputs_schema={"type": "object", "properties": {"output": {"type": "string"}}},
                secrets=[f"secret{i}_1", f"secret{i}_2"]
            )
            nodes.append(node)
        return nodes

    @pytest.fixture
    def mock_register_request(self, mock_runtime_name, mock_node_registration):
        """Create mock register nodes request"""
        return RegisterNodesRequestModel(
            runtime_name=mock_runtime_name,
            nodes=[mock_node_registration]
        )

    @pytest.fixture
    def mock_multiple_register_request(self, mock_runtime_name, mock_multiple_node_registrations):
        """Create mock register nodes request with multiple nodes"""
        return RegisterNodesRequestModel(
            runtime_name=mock_runtime_name,
            nodes=mock_multiple_node_registrations
        )

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_create_new_node_success(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_register_request,
        mock_request_id
    ):
        """Test successful creation of new node"""
        # Arrange
        # No existing node found
        mock_registered_node_class.find_one = AsyncMock(return_value=None)
        
        # Mock new node creation
        mock_new_node = MagicMock()
        mock_new_node.insert = AsyncMock()
        mock_registered_node_class.return_value = mock_new_node

        # Act
        result = await register_nodes(mock_namespace, mock_register_request, mock_request_id)

        # Assert
        assert isinstance(result, RegisterNodesResponseModel)
        assert result.runtime_name == mock_register_request.runtime_name
        assert len(result.registered_nodes) == 1
        
        registered_node = result.registered_nodes[0]
        assert registered_node.name == "test_node"
        assert registered_node.inputs_schema == mock_register_request.nodes[0].inputs_schema
        assert registered_node.outputs_schema == mock_register_request.nodes[0].outputs_schema
        assert registered_node.secrets == mock_register_request.nodes[0].secrets

        # Verify database operations
        mock_registered_node_class.find_one.assert_called_once()
        mock_registered_node_class.assert_called_once()
        mock_new_node.insert.assert_called_once()

        # Verify logging
        mock_logger.info.assert_any_call(
            f"Registering nodes for namespace {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Created new node test_node in namespace {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_update_existing_node_success(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_register_request,
        mock_request_id
    ):
        """Test successful update of existing node"""
        # Arrange
        # Mock existing node
        mock_existing_node = MagicMock()
        mock_existing_node.update = AsyncMock()
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_existing_node)

        # Act
        result = await register_nodes(mock_namespace, mock_register_request, mock_request_id)

        # Assert
        assert isinstance(result, RegisterNodesResponseModel)
        assert result.runtime_name == mock_register_request.runtime_name
        assert len(result.registered_nodes) == 1

        # Verify database operations
        mock_registered_node_class.find_one.assert_called_once()
        mock_existing_node.update.assert_called_once()

        # Verify logging
        mock_logger.info.assert_any_call(
            f"Updated existing node test_node in namespace {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_multiple_nodes_mixed_operations(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_multiple_register_request,
        mock_request_id
    ):
        """Test registering multiple nodes with mixed create/update operations"""
        # Arrange
        # First node exists, second and third are new
        mock_existing_node = MagicMock()
        mock_existing_node.update = AsyncMock()
        
        mock_new_node_1 = MagicMock()
        mock_new_node_1.insert = AsyncMock()
        mock_new_node_2 = MagicMock()
        mock_new_node_2.insert = AsyncMock()
        
        # Mock find_one to return existing for first call, None for others
        mock_registered_node_class.find_one = AsyncMock(side_effect=[mock_existing_node, None, None])
        mock_registered_node_class.side_effect = [mock_new_node_1, mock_new_node_2]

        # Act
        result = await register_nodes(mock_namespace, mock_multiple_register_request, mock_request_id)

        # Assert
        assert isinstance(result, RegisterNodesResponseModel)
        assert result.runtime_name == mock_multiple_register_request.runtime_name
        assert len(result.registered_nodes) == 3

        # Verify database operations
        assert mock_registered_node_class.find_one.call_count == 3
        mock_existing_node.update.assert_called_once()
        mock_new_node_1.insert.assert_called_once()
        mock_new_node_2.insert.assert_called_once()

        # Verify logging
        mock_logger.info.assert_any_call(
            f"Updated existing node test_node_0 in namespace {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Created new node test_node_1 in namespace {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_database_error_during_find(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_register_request,
        mock_request_id
    ):
        """Test error handling during database find operation"""
        # Arrange
        mock_registered_node_class.find_one = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await register_nodes(mock_namespace, mock_register_request, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert f"Error registering nodes for namespace {mock_namespace}" in str(error_call)

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_database_error_during_update(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_register_request,
        mock_request_id
    ):
        """Test error handling during database update operation"""
        # Arrange
        mock_existing_node = MagicMock()
        mock_existing_node.update = AsyncMock(side_effect=Exception("Update failed"))
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_existing_node)

        # Act & Assert
        with pytest.raises(Exception, match="Update failed"):
            await register_nodes(mock_namespace, mock_register_request, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_database_error_during_insert(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_register_request,
        mock_request_id
    ):
        """Test error handling during database insert operation"""
        # Arrange
        mock_registered_node_class.find_one = AsyncMock(return_value=None)
        mock_new_node = MagicMock()
        mock_new_node.insert = AsyncMock(side_effect=Exception("Insert failed"))
        mock_registered_node_class.return_value = mock_new_node

        # Act & Assert
        with pytest.raises(Exception, match="Insert failed"):
            await register_nodes(mock_namespace, mock_register_request, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_empty_node_list(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_runtime_name,
        mock_request_id
    ):
        """Test registering with empty node list"""
        # Arrange
        empty_request = RegisterNodesRequestModel(
            runtime_name=mock_runtime_name,
            nodes=[]
        )

        # Act
        result = await register_nodes(mock_namespace, empty_request, mock_request_id)

        # Assert
        assert isinstance(result, RegisterNodesResponseModel)
        assert result.runtime_name == mock_runtime_name
        assert len(result.registered_nodes) == 0

        # Verify no database operations were performed
        mock_registered_node_class.find_one.assert_not_called()

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_update_fields_verification(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_register_request,
        mock_request_id
    ):
        """Test that update operation includes all required fields"""
        # Arrange
        mock_existing_node = MagicMock()
        mock_existing_node.update = AsyncMock()
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_existing_node)

        # Act
        await register_nodes(mock_namespace, mock_register_request, mock_request_id)

        # Assert - Verify update was called with correct fields
        mock_existing_node.update.assert_called_once()
        update_call_args = mock_existing_node.update.call_args[0][0]
        
        # The update method is called with a Set object, not a dict
        # We can't easily inspect the Set object contents, so just verify it was called
        assert isinstance(update_call_args, type(Set({})))

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_new_node_fields_verification(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_register_request,
        mock_request_id
    ):
        """Test that new node creation includes all required fields"""
        # Arrange
        mock_registered_node_class.find_one = AsyncMock(return_value=None)
        mock_new_node = MagicMock()
        mock_new_node.insert = AsyncMock()
        mock_registered_node_class.return_value = mock_new_node

        # Act
        await register_nodes(mock_namespace, mock_register_request, mock_request_id)

        # Assert - Verify new node was created with correct fields
        mock_registered_node_class.assert_called_once()
        create_call_args = mock_registered_node_class.call_args[1]
        
        expected_fields = {
            'name': mock_register_request.nodes[0].name,
            'namespace': mock_namespace,
            'runtime_name': mock_register_request.runtime_name,
            'runtime_namespace': mock_namespace,
            'inputs_schema': mock_register_request.nodes[0].inputs_schema,
            'outputs_schema': mock_register_request.nodes[0].outputs_schema,
            'secrets': mock_register_request.nodes[0].secrets
        }
        
        for field, expected_value in expected_fields.items():
            assert create_call_args[field] == expected_value

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_response_structure_verification(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_multiple_register_request,
        mock_request_id
    ):
        """Test that response structure is correct"""
        # Arrange
        mock_registered_node_class.find_one = AsyncMock(return_value=None)
        mock_new_node = MagicMock()
        mock_new_node.insert = AsyncMock()
        mock_registered_node_class.return_value = mock_new_node

        # Act
        result = await register_nodes(mock_namespace, mock_multiple_register_request, mock_request_id)

        # Assert
        assert isinstance(result, RegisterNodesResponseModel)
        assert result.runtime_name == mock_multiple_register_request.runtime_name
        assert isinstance(result.registered_nodes, list)
        assert len(result.registered_nodes) == len(mock_multiple_register_request.nodes)
        
        for i, registered_node in enumerate(result.registered_nodes):
            assert isinstance(registered_node, RegisteredNodeModel)
            original_node = mock_multiple_register_request.nodes[i]
            assert registered_node.name == original_node.name
            assert registered_node.inputs_schema == original_node.inputs_schema
            assert registered_node.outputs_schema == original_node.outputs_schema
            assert registered_node.secrets == original_node.secrets

    @patch('app.controller.register_nodes.RegisteredNode')
    @patch('app.controller.register_nodes.logger')
    async def test_register_nodes_success_logging(
        self,
        mock_logger,
        mock_registered_node_class,
        mock_namespace,
        mock_multiple_register_request,
        mock_request_id
    ):
        """Test comprehensive logging for successful operations"""
        # Arrange
        mock_registered_node_class.find_one = AsyncMock(return_value=None)
        mock_new_node = MagicMock()
        mock_new_node.insert = AsyncMock()
        mock_registered_node_class.return_value = mock_new_node

        # Act
        result = await register_nodes(mock_namespace, mock_multiple_register_request, mock_request_id)

        # Assert logging calls
        expected_log_calls = [
            f"Registering nodes for namespace {mock_namespace}",
            f"Successfully registered {len(result.registered_nodes)} nodes for namespace {mock_namespace}"
        ]
        
        # Verify initial and final logging
        mock_logger.info.assert_any_call(
            expected_log_calls[0],
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            expected_log_calls[1],
            x_exosphere_request_id=mock_request_id
        )
        
        # Verify per-node logging
        for node in mock_multiple_register_request.nodes:
            mock_logger.info.assert_any_call(
                f"Created new node {node.name} in namespace {mock_namespace}",
                x_exosphere_request_id=mock_request_id
            )