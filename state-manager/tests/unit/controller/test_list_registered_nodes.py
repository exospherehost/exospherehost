import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.controller.list_registered_nodes import list_registered_nodes
from app.models.db.registered_node import RegisteredNode


class TestListRegisteredNodes:
    """Test cases for list_registered_nodes function"""

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_registered_nodes(self):
        """Create mock registered nodes for testing"""
        nodes = []
        for i in range(3):
            node = MagicMock(spec=RegisteredNode)
            node.id = f"node_id_{i}"
            node.name = f"test_node_{i}"
            node.namespace = "test_namespace"
            node.runtime_name = f"runtime_{i}"
            node.runtime_namespace = "test_namespace"
            node.inputs_schema = {"type": "object", "properties": {"input": {"type": "string"}}}
            node.outputs_schema = {"type": "object", "properties": {"output": {"type": "string"}}}
            node.secrets = ["secret1", "secret2"]
            nodes.append(node)
        return nodes

    @patch('app.controller.list_registered_nodes.RegisteredNode')
    @patch('app.controller.list_registered_nodes.LogsManager')
    async def test_list_registered_nodes_success(
        self,
        mock_logs_manager,
        mock_registered_node_class,
        mock_namespace,
        mock_request_id,
        mock_registered_nodes
    ):
        """Test successful retrieval of registered nodes"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_registered_nodes)
        mock_registered_node_class.find.return_value = mock_query

        # Act
        result = await list_registered_nodes(mock_namespace, mock_request_id)

        # Assert
        assert result == mock_registered_nodes
        assert len(result) == 3
        mock_registered_node_class.find.assert_called_once()
        mock_query.to_list.assert_called_once()
        
        # Verify logging
        mock_logger.info.assert_any_call(
            f"Listing registered nodes for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Found {len(mock_registered_nodes)} registered nodes for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.list_registered_nodes.RegisteredNode')
    @patch('app.controller.list_registered_nodes.LogsManager')
    async def test_list_registered_nodes_empty_result(
        self,
        mock_logs_manager,
        mock_registered_node_class,
        mock_namespace,
        mock_request_id
    ):
        """Test when no registered nodes are found"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_registered_node_class.find.return_value = mock_query

        # Act
        result = await list_registered_nodes(mock_namespace, mock_request_id)

        # Assert
        assert result == []
        assert len(result) == 0
        mock_registered_node_class.find.assert_called_once()
        mock_query.to_list.assert_called_once()
        
        # Verify logging
        mock_logger.info.assert_any_call(
            f"Listing registered nodes for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Found 0 registered nodes for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.list_registered_nodes.RegisteredNode')
    @patch('app.controller.list_registered_nodes.LogsManager')
    async def test_list_registered_nodes_database_error(
        self,
        mock_logs_manager,
        mock_registered_node_class,
        mock_namespace,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(side_effect=Exception("Database connection error"))
        mock_registered_node_class.find.return_value = mock_query

        # Act & Assert
        with pytest.raises(Exception, match="Database connection error"):
            await list_registered_nodes(mock_namespace, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert "Error listing registered nodes for namespace test_namespace" in str(error_call)

    @patch('app.controller.list_registered_nodes.RegisteredNode')
    @patch('app.controller.list_registered_nodes.LogsManager')
    async def test_list_registered_nodes_find_error(
        self,
        mock_logs_manager,
        mock_registered_node_class,
        mock_namespace,
        mock_request_id
    ):
        """Test error during RegisteredNode.find operation"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_registered_node_class.find.side_effect = Exception("Find operation failed")

        # Act & Assert
        with pytest.raises(Exception, match="Find operation failed"):
            await list_registered_nodes(mock_namespace, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()

    @patch('app.controller.list_registered_nodes.RegisteredNode')
    @patch('app.controller.list_registered_nodes.LogsManager')
    async def test_list_registered_nodes_filter_criteria(
        self,
        mock_logs_manager,
        mock_registered_node_class,
        mock_namespace,
        mock_request_id,
        mock_registered_nodes
    ):
        """Test that the correct filter criteria are used"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_registered_nodes)
        mock_registered_node_class.find.return_value = mock_query

        # Act
        await list_registered_nodes(mock_namespace, mock_request_id)

        # Assert that RegisteredNode.find was called with the correct namespace filter
        mock_registered_node_class.find.assert_called_once()
        call_args = mock_registered_node_class.find.call_args[0]
        # The filter should match the namespace
        assert len(call_args) == 1  # Should have one filter condition

    @patch('app.controller.list_registered_nodes.RegisteredNode')
    @patch('app.controller.list_registered_nodes.LogsManager')
    async def test_list_registered_nodes_different_namespaces(
        self,
        mock_logs_manager,
        mock_registered_node_class,
        mock_request_id
    ):
        """Test with different namespace values"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_registered_node_class.find.return_value = mock_query

        namespaces = ["prod", "staging", "dev", "test-123", ""]

        # Act & Assert
        for namespace in namespaces:
            mock_registered_node_class.reset_mock()
            mock_logger.reset_mock()
            
            result = await list_registered_nodes(namespace, mock_request_id)
            
            assert result == []
            mock_registered_node_class.find.assert_called_once()
            mock_logger.info.assert_any_call(
                f"Listing registered nodes for namespace: {namespace}",
                x_exosphere_request_id=mock_request_id
            )

    @patch('app.controller.list_registered_nodes.RegisteredNode')
    @patch('app.controller.list_registered_nodes.LogsManager')
    async def test_list_registered_nodes_large_result_set(
        self,
        mock_logs_manager,
        mock_registered_node_class,
        mock_namespace,
        mock_request_id
    ):
        """Test with large number of registered nodes"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        # Create large number of mock nodes
        large_nodes_list = []
        for i in range(500):
            node = MagicMock(spec=RegisteredNode)
            node.id = f"node_{i}"
            node.name = f"node_{i}"
            node.namespace = mock_namespace
            large_nodes_list.append(node)
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=large_nodes_list)
        mock_registered_node_class.find.return_value = mock_query

        # Act
        result = await list_registered_nodes(mock_namespace, mock_request_id)

        # Assert
        assert len(result) == 500
        mock_logger.info.assert_any_call(
            f"Found 500 registered nodes for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.list_registered_nodes.RegisteredNode')
    @patch('app.controller.list_registered_nodes.LogsManager')
    async def test_list_registered_nodes_return_type(
        self,
        mock_logs_manager,
        mock_registered_node_class,
        mock_namespace,
        mock_request_id,
        mock_registered_nodes
    ):
        """Test that the function returns the correct type"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_registered_nodes)
        mock_registered_node_class.find.return_value = mock_query

        # Act
        result = await list_registered_nodes(mock_namespace, mock_request_id)

        # Assert
        assert isinstance(result, list)
        for node in result:
            assert isinstance(node, MagicMock)  # Since we're using mocks
        
        # Verify each node has expected attributes (via mock)
        for node in result:
            assert hasattr(node, 'id')
            assert hasattr(node, 'name')
            assert hasattr(node, 'namespace')

    @patch('app.controller.list_registered_nodes.RegisteredNode')
    @patch('app.controller.list_registered_nodes.LogsManager')
    async def test_list_registered_nodes_concurrent_requests(
        self,
        mock_logs_manager,
        mock_registered_node_class,
        mock_request_id
    ):
        """Test handling concurrent requests with different namespaces"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_registered_node_class.find.return_value = mock_query

        # Simulate concurrent requests to different namespaces
        namespaces = ["namespace1", "namespace2", "namespace3"]
        
        # Act
        import asyncio
        tasks = [list_registered_nodes(ns, f"{mock_request_id}_{i}") for i, ns in enumerate(namespaces)]
        results = await asyncio.gather(*tasks)

        # Assert
        assert len(results) == 3
        for result in results:
            assert result == []
        
        # Each namespace should have been queried
        assert mock_registered_node_class.find.call_count == 3