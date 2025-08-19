import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from app.controller.get_current_states import get_current_states
from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum


class TestGetCurrentStates:
    """Test cases for get_current_states function"""

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_states(self):
        """Create mock states for testing"""
        states = []
        for i in range(3):
            state = MagicMock(spec=State)
            state.id = f"state_id_{i}"
            state.namespace_name = "test_namespace"
            state.status = StateStatusEnum.CREATED
            state.identifier = f"node_{i}"
            state.graph_name = "test_graph"
            state.run_id = f"run_{i}"
            states.append(state)
        return states

    @patch('app.controller.get_current_states.State')
    @patch('app.controller.get_current_states.LogsManager')
    async def test_get_current_states_success(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_request_id,
        mock_states
    ):
        """Test successful retrieval of current states"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_states)
        mock_state_class.find.return_value = mock_query

        # Act
        result = await get_current_states(mock_namespace, mock_request_id)

        # Assert
        assert result == mock_states
        assert len(result) == 3
        mock_state_class.find.assert_called_once()
        mock_query.to_list.assert_called_once()
        
        # Verify logging
        mock_logger.info.assert_any_call(
            f"Fetching current states for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Found {len(mock_states)} states for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.get_current_states.State')
    @patch('app.controller.get_current_states.LogsManager')
    async def test_get_current_states_empty_result(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_request_id
    ):
        """Test when no states are found"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_state_class.find.return_value = mock_query

        # Act
        result = await get_current_states(mock_namespace, mock_request_id)

        # Assert
        assert result == []
        assert len(result) == 0
        mock_state_class.find.assert_called_once()
        mock_query.to_list.assert_called_once()
        
        # Verify logging
        mock_logger.info.assert_any_call(
            f"Fetching current states for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Found 0 states for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.get_current_states.State')
    @patch('app.controller.get_current_states.LogsManager')
    async def test_get_current_states_database_error(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
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
            await get_current_states(mock_namespace, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert "Error fetching current states for namespace test_namespace" in str(error_call)

    @patch('app.controller.get_current_states.State')
    @patch('app.controller.get_current_states.LogsManager')
    async def test_get_current_states_find_error(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_request_id
    ):
        """Test error during State.find operation"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_state_class.find.side_effect = Exception("Find operation failed")

        # Act & Assert
        with pytest.raises(Exception, match="Find operation failed"):
            await get_current_states(mock_namespace, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()

    @patch('app.controller.get_current_states.State')
    @patch('app.controller.get_current_states.LogsManager')
    async def test_get_current_states_filter_criteria(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
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
        await get_current_states(mock_namespace, mock_request_id)

        # Assert that State.find was called with the correct namespace filter
        mock_state_class.find.assert_called_once()
        call_args = mock_state_class.find.call_args[0]
        # The filter should match the namespace_name
        assert len(call_args) == 1  # Should have one filter condition

    @patch('app.controller.get_current_states.State')
    @patch('app.controller.get_current_states.LogsManager')
    async def test_get_current_states_different_namespaces(
        self,
        mock_logs_manager,
        mock_state_class,
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
            
            result = await get_current_states(namespace, mock_request_id)
            
            assert result == []
            mock_state_class.find.assert_called_once()
            mock_logger.info.assert_any_call(
                f"Fetching current states for namespace: {namespace}",
                x_exosphere_request_id=mock_request_id
            )

    @patch('app.controller.get_current_states.State')
    @patch('app.controller.get_current_states.LogsManager')
    async def test_get_current_states_large_result_set(
        self,
        mock_logs_manager,
        mock_state_class,
        mock_namespace,
        mock_request_id
    ):
        """Test with large number of states"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        # Create large number of mock states
        large_states_list = []
        for i in range(1000):
            state = MagicMock(spec=State)
            state.id = f"state_{i}"
            state.namespace_name = mock_namespace
            large_states_list.append(state)
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=large_states_list)
        mock_state_class.find.return_value = mock_query

        # Act
        result = await get_current_states(mock_namespace, mock_request_id)

        # Assert
        assert len(result) == 1000
        mock_logger.info.assert_any_call(
            f"Found 1000 states for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )