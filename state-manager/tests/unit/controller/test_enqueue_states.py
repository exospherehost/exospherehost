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

    @patch('app.controller.enqueue_states.State')
    async def test_enqueue_states_success(
        self,
        mock_state_class,
        mock_namespace,
        mock_enqueue_request,
        mock_state,
        mock_request_id
    ):
        """Test successful enqueuing of states"""
        # Arrange
        # Mock State.find().limit().to_list() chain
        mock_query = MagicMock()
        mock_query.limit = MagicMock(return_value=mock_query)
        mock_query.to_list = AsyncMock(return_value=[mock_state])
        
        # Mock State.find().set() chain for updating states
        mock_update_query = MagicMock()
        mock_update_query.set = AsyncMock()
        
        # Configure State.find to return different mocks based on call
        mock_state_class.find = MagicMock()
        mock_state_class.find.side_effect = [mock_query, mock_update_query]

        # Act
        result = await enqueue_states(
            mock_namespace,
            mock_enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.count == 1
        assert result.namespace == mock_namespace
        assert result.status == StateStatusEnum.QUEUED
        assert len(result.states) == 1
        assert result.states[0].state_id == str(mock_state.id)
        assert result.states[0].node_name == "node1"
        assert result.states[0].identifier == "test_identifier"
        assert result.states[0].inputs == {"key": "value"}

        # Verify the find query was called correctly
        assert mock_state_class.find.call_count == 2  # Called twice: once for finding, once for updating
        mock_query.limit.assert_called_once_with(10)
        mock_update_query.set.assert_called_once()

    @patch('app.controller.enqueue_states.State')
    async def test_enqueue_states_no_states_found(
        self,
        mock_state_class,
        mock_namespace,
        mock_enqueue_request,
        mock_request_id
    ):
        """Test when no states are found to enqueue"""
        # Arrange
        mock_query = MagicMock()
        mock_query.limit = MagicMock(return_value=mock_query)
        mock_query.to_list = AsyncMock(return_value=[])
        
        # When no states are found, the second State.find() call won't happen
        mock_state_class.find = MagicMock(return_value=mock_query)

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

    @patch('app.controller.enqueue_states.State')
    async def test_enqueue_states_multiple_states(
        self,
        mock_state_class,
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

        mock_query = MagicMock()
        mock_query.limit = MagicMock(return_value=mock_query)
        mock_query.to_list = AsyncMock(return_value=[state1, state2])
        
        # Mock State.find().set() chain for updating states
        mock_update_query = MagicMock()
        mock_update_query.set = AsyncMock()
        
        # Configure State.find to return different mocks based on call
        mock_state_class.find = MagicMock()
        mock_state_class.find.side_effect = [mock_query, mock_update_query]

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

    @patch('app.controller.enqueue_states.State')
    async def test_enqueue_states_database_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_enqueue_request,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_state_class.find = MagicMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await enqueue_states(
                mock_namespace,
                mock_enqueue_request,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Database error"

    @patch('app.controller.enqueue_states.State')
    async def test_enqueue_states_with_different_batch_size(
        self,
        mock_state_class,
        mock_namespace,
        mock_request_id
    ):
        """Test enqueuing with different batch sizes"""
        # Arrange
        enqueue_request = EnqueueRequestModel(
            nodes=["node1"],
            batch_size=5
        )

        mock_query = MagicMock()
        mock_query.limit = MagicMock(return_value=mock_query)
        mock_query.to_list = AsyncMock(return_value=[])
        
        # When no states are found, the second State.find() call won't happen
        mock_state_class.find = MagicMock(return_value=mock_query)

        # Act
        result = await enqueue_states(
            mock_namespace,
            enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.count == 0
        mock_query.limit.assert_called_once_with(5)
