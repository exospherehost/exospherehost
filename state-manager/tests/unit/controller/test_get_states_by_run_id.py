import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from app.controller.get_states_by_run_id import get_states_by_run_id
from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum


class TestGetStatesByRunId:
    """Test cases for get_states_by_run_id function"""

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_run_id(self):
        return "test-run-id-123"

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_states(self, mock_namespace, mock_run_id):
        """Create mock states for testing"""
        states = []
        for i in range(4):
            state = MagicMock(spec=State)
            state.id = f"state_id_{i}"
            state.namespace_name = mock_namespace
            state.run_id = mock_run_id
            state.status = StateStatusEnum.CREATED if i % 2 == 0 else StateStatusEnum.EXECUTED
            state.identifier = f"node_{i}"
            state.graph_name = "test_graph"
            states.append(state)
        return states

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_success(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_run_id,
        mock_request_id,
        mock_states
    ):
        """Test successful retrieval of states by run ID"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_states)
        mock_state_class.find.return_value = mock_query

        # Act
        result = await get_states_by_run_id(mock_namespace, mock_run_id, mock_request_id)

        # Assert
        assert result == mock_states
        assert len(result) == 4
        mock_state_class.find.assert_called_once()
        mock_query.to_list.assert_called_once()
        
        # Verify logging
        mock_logger.info.assert_any_call(
            f"Fetching states for run ID: {mock_run_id} in namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Found {len(mock_states)} states for run ID: {mock_run_id}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_empty_result(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_run_id,
        mock_request_id
    ):
        """Test when no states are found for the run ID"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_state_class.find.return_value = mock_query

        # Act
        result = await get_states_by_run_id(mock_namespace, mock_run_id, mock_request_id)

        # Assert
        assert result == []
        assert len(result) == 0
        mock_state_class.find.assert_called_once()
        mock_query.to_list.assert_called_once()
        
        # Verify logging
        mock_logger.info.assert_any_call(
            f"Fetching states for run ID: {mock_run_id} in namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Found 0 states for run ID: {mock_run_id}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_database_error(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_run_id,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(side_effect=Exception("Database connection error"))
        mock_state_class.find.return_value = mock_query

        # Act & Assert
        with pytest.raises(Exception, match="Database connection error"):
            await get_states_by_run_id(mock_namespace, mock_run_id, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert f"Error fetching states for run ID {mock_run_id} in namespace {mock_namespace}" in str(error_call)

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_find_error(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_run_id,
        mock_request_id
    ):
        """Test error during State.find operation"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_state_class.find.side_effect = Exception("Find operation failed")

        # Act & Assert
        with pytest.raises(Exception, match="Find operation failed"):
            await get_states_by_run_id(mock_namespace, mock_run_id, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_filter_criteria(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_run_id,
        mock_request_id,
        mock_states
    ):
        """Test that the correct filter criteria are used"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_states)
        mock_state_class.find.return_value = mock_query

        # Act
        await get_states_by_run_id(mock_namespace, mock_run_id, mock_request_id)

        # Assert that State.find was called with correct filters
        mock_state_class.find.assert_called_once()
        call_args = mock_state_class.find.call_args[0]
        # Should have two filter conditions: run_id and namespace_name
        assert len(call_args) == 2

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_different_run_ids(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_request_id
    ):
        """Test with different run ID values"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_state_class.find.return_value = mock_query

        run_ids = ["run-123", "run-abc-456", "test_run_789", "run-with-special-chars-!@#", ""]

        # Act & Assert
        for run_id in run_ids:
            mock_state_class.reset_mock()
            mock_logger.reset_mock()
            
            result = await get_states_by_run_id(mock_namespace, run_id, mock_request_id)
            
            assert result == []
            mock_state_class.find.assert_called_once()
            mock_logger.info.assert_any_call(
                f"Fetching states for run ID: {run_id} in namespace: {mock_namespace}",
                x_exosphere_request_id=mock_request_id
            )

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_different_namespaces(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_run_id,
        mock_request_id
    ):
        """Test with different namespace values"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_state_class.find.return_value = mock_query

        namespaces = ["prod", "staging", "dev", "test-123", ""]

        # Act & Assert
        for namespace in namespaces:
            mock_state_class.reset_mock()
            mock_logger.reset_mock()
            
            result = await get_states_by_run_id(namespace, mock_run_id, mock_request_id)
            
            assert result == []
            mock_state_class.find.assert_called_once()
            mock_logger.info.assert_any_call(
                f"Fetching states for run ID: {mock_run_id} in namespace: {namespace}",
                x_exosphere_request_id=mock_request_id
            )

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_large_result_set(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_run_id,
        mock_request_id
    ):
        """Test with large number of states"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        # Create large number of mock states
        large_states_list = []
        for i in range(1500):
            state = MagicMock(spec=State)
            state.id = f"state_{i}"
            state.namespace_name = mock_namespace
            state.run_id = mock_run_id
            large_states_list.append(state)
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=large_states_list)
        mock_state_class.find.return_value = mock_query

        # Act
        result = await get_states_by_run_id(mock_namespace, mock_run_id, mock_request_id)

        # Assert
        assert len(result) == 1500
        mock_logger.info.assert_any_call(
            f"Found 1500 states for run ID: {mock_run_id}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_return_type(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_run_id,
        mock_request_id,
        mock_states
    ):
        """Test that the function returns the correct type"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_states)
        mock_state_class.find.return_value = mock_query

        # Act
        result = await get_states_by_run_id(mock_namespace, mock_run_id, mock_request_id)

        # Assert
        assert isinstance(result, list)
        for state in result:
            assert isinstance(state, MagicMock)  # Since we're using mocks
        
        # Verify each state has expected attributes
        for state in result:
            assert hasattr(state, 'id')
            assert hasattr(state, 'namespace_name')
            assert hasattr(state, 'run_id')
            assert state.namespace_name == mock_namespace
            assert state.run_id == mock_run_id

    @patch('app.controller.get_states_by_run_id.State')
    @patch('app.controller.get_states_by_run_id.LogsManager')
    async def test_get_states_by_run_id_single_state(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_run_id,
        mock_request_id
    ):
        """Test with single state result"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        single_state = MagicMock(spec=State)
        single_state.id = "single_state_id"
        single_state.namespace_name = mock_namespace
        single_state.run_id = mock_run_id
        single_state.status = StateStatusEnum.SUCCESS
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[single_state])
        mock_state_class.find.return_value = mock_query

        # Act
        result = await get_states_by_run_id(mock_namespace, mock_run_id, mock_request_id)

        # Assert
        assert len(result) == 1
        assert result[0] == single_state
        mock_logger.info.assert_any_call(
            f"Found 1 states for run ID: {mock_run_id}",
            x_exosphere_request_id=mock_request_id
        )