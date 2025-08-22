import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from beanie import PydanticObjectId
from datetime import datetime

from app.controller.enqueue_states import enqueue_states
from app.models.enqueue_request import EnqueueRequestModel
from app.models.state_status_enum import StateStatusEnum


class TestEnqueueStates:
    """Test cases for enqueue_states function"""

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_enqueue_request(self):
        return EnqueueRequestModel(
            nodes=["node1", "node2"],
            batch_size=10
        )

    @pytest.fixture
    def mock_state(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.node_name = "node1"
        state.identifier = "test_identifier"
        state.inputs = {"key": "value"}
        state.created_at = datetime.now()
        return state

    @patch('app.controller.enqueue_states.find_state')
    async def test_enqueue_states_success(
        self,
        mock_find_state,
        mock_namespace,
        mock_enqueue_request,
        mock_state,
        mock_request_id
    ):
        """Test successful enqueuing of states"""
        # Arrange
        # Mock find_state to return the mock_state for all calls
        mock_find_state.return_value = mock_state

        # Act
        result = await enqueue_states(
            mock_namespace,
            mock_enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.count == 10  # batch_size=10, so 10 states should be returned
        assert result.namespace == mock_namespace
        assert result.status == StateStatusEnum.QUEUED
        assert len(result.states) == 10
        assert result.states[0].state_id == str(mock_state.id)
        assert result.states[0].node_name == "node1"
        assert result.states[0].identifier == "test_identifier"
        assert result.states[0].inputs == {"key": "value"}

        # Verify find_state was called correctly
        assert mock_find_state.call_count == 10  # Called batch_size times
        mock_find_state.assert_called_with(mock_namespace, ["node1", "node2"])

    @patch('app.controller.enqueue_states.find_state')
    async def test_enqueue_states_no_states_found(
        self,
        mock_find_state,
        mock_namespace,
        mock_enqueue_request,
        mock_request_id
    ):
        """Test when no states are found to enqueue"""
        # Arrange
        # Mock find_state to return None for all calls
        mock_find_state.return_value = None

        # Act
        result = await enqueue_states(
            mock_namespace,
            mock_enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.count == 0
        assert result.namespace == mock_namespace
        assert result.status == StateStatusEnum.QUEUED
        assert len(result.states) == 0

    @patch('app.controller.enqueue_states.find_state')
    async def test_enqueue_states_multiple_states(
        self,
        mock_find_state,
        mock_namespace,
        mock_enqueue_request,
        mock_request_id
    ):
        """Test enqueuing multiple states"""
        # Arrange
        state1 = MagicMock()
        state1.id = PydanticObjectId()
        state1.node_name = "node1"
        state1.identifier = "identifier1"
        state1.inputs = {"input1": "value1"}
        state1.created_at = datetime.now()

        state2 = MagicMock()
        state2.id = PydanticObjectId()
        state2.node_name = "node2"
        state2.identifier = "identifier2"
        state2.inputs = {"input2": "value2"}
        state2.created_at = datetime.now()

        # Mock find_state to return different states
        mock_find_state.side_effect = [state1, state2, None, None, None, None, None, None, None, None]

        # Act
        result = await enqueue_states(
            mock_namespace,
            mock_enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.count == 2
        assert len(result.states) == 2
        assert result.states[0].node_name == "node1"
        assert result.states[1].node_name == "node2"

    @patch('app.controller.enqueue_states.find_state')
    async def test_enqueue_states_database_error(
        self,
        mock_find_state,
        mock_namespace,
        mock_enqueue_request,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        # Mock find_state to raise an exception
        mock_find_state.side_effect = Exception("Database error")

        # Act
        result = await enqueue_states(
            mock_namespace,
            mock_enqueue_request,
            mock_request_id
        )

        # Assert - the function should handle exceptions gracefully and return empty result
        assert result.count == 0
        assert result.namespace == mock_namespace
        assert result.status == StateStatusEnum.QUEUED
        assert len(result.states) == 0

    @patch('app.controller.enqueue_states.find_state')
    async def test_enqueue_states_with_different_batch_size(
        self,
        mock_find_state,
        mock_namespace,
        mock_request_id
    ):
        """Test enqueuing with different batch sizes"""
        # Arrange
        enqueue_request = EnqueueRequestModel(
            nodes=["node1"],
            batch_size=5
        )

        # Mock find_state to return None
        mock_find_state.return_value = None

        # Act
        result = await enqueue_states(
            mock_namespace,
            enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.count == 0
        assert mock_find_state.call_count == 5  # Called batch_size times
