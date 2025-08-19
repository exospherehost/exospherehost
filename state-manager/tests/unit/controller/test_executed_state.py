import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from app.controller.executed_state import executed_state
from app.models.executed_models import ExecutedRequestModel
from app.models.state_status_enum import StateStatusEnum


class TestExecutedState:
    """Test cases for executed_state function"""

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_state_id(self):
        return PydanticObjectId()

    @pytest.fixture
    def mock_background_tasks(self):
        return MagicMock()

    @pytest.fixture
    def mock_state(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.status = StateStatusEnum.QUEUED
        state.node_name = "test_node"
        state.namespace_name = "test_namespace"
        state.identifier = "test_identifier"
        state.graph_name = "test_graph"
        state.inputs = {"key": "value"}
        state.parents = {}
        return state

    @pytest.fixture
    def mock_executed_request(self):
        return ExecutedRequestModel(
            outputs=[{"result": "success"}]
        )

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    async def test_executed_state_success_single_output(
        self,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_executed_request,
        mock_state,
        mock_background_tasks,
        mock_request_id
    ):
        """Test successful execution of state with single output"""
        # Arrange
        # Mock State.find_one() for finding the state
        # Mock State.find_one().set() for updating the state
        mock_update_query = MagicMock()
        mock_update_query.set = AsyncMock()

        mock_state.save = AsyncMock()

        mock_state.status = StateStatusEnum.QUEUED 
        mock_state.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state)   

        # Act
        result = await executed_state(
            mock_namespace,
            mock_state_id,
            mock_executed_request,
            mock_request_id,
            mock_background_tasks
        )

        # Assert
        assert result.status == StateStatusEnum.EXECUTED
        assert mock_state_class.find_one.call_count == 1  # Called once for finding
        mock_background_tasks.add_task.assert_called_once_with(mock_create_next_states, [mock_state.id], mock_state.identifier, mock_state.namespace_name, mock_state.graph_name, mock_state.parents)

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    async def test_executed_state_success_multiple_outputs(
        self,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_background_tasks,
        mock_request_id
    ):
        """Test successful execution of state with multiple outputs"""
        # Arrange
        executed_request = ExecutedRequestModel(
            outputs=[
                {"result": "success1"},
                {"result": "success2"},
                {"result": "success3"}
            ]
        )

        # Mock State.find_one() for finding the state
        # Mock State.find_one().set() for updating the state
        mock_update_query = MagicMock()
        mock_update_query.set = AsyncMock()
        
        # Configure State.find_one to return different values based on call
        # First call returns the state object, second call returns a query object with set method
        # Additional calls in the loop also return query objects with set method
        mock_state_class.find_one = AsyncMock(return_value=mock_state)
        mock_state.save = AsyncMock()
        new_ids = [PydanticObjectId(), PydanticObjectId()]
        mock_state_class.insert_many = AsyncMock(return_value=MagicMock(inserted_ids=new_ids))
        mock_state_class.find = MagicMock(return_value=AsyncMock(to_list=AsyncMock(return_value=[mock_state, mock_state])))
        
        # Mock State.save() for new states
        mock_new_state = MagicMock()
        mock_new_state.save = AsyncMock()
        mock_state_class.return_value = mock_new_state

        # Act
        result = await executed_state(
            mock_namespace,
            mock_state_id,
            executed_request,
            mock_request_id,
            mock_background_tasks
        )

        # Assert
        assert result.status == StateStatusEnum.EXECUTED
        # Should create 2 additional states (3 outputs total, 1 for main state, 2 new states)
        assert mock_state_class.call_count == 2
        # Should add 1 background task with all state IDs
        assert mock_background_tasks.add_task.call_count == 1
        # State.find_one should be called once for finding the state
        assert mock_state_class.find_one.call_count == 1

    @patch('app.controller.executed_state.State')
    async def test_executed_state_not_found(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_executed_request,
        mock_background_tasks,
        mock_request_id
    ):
        """Test when state is not found"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await executed_state(
                mock_namespace,
                mock_state_id,
                mock_executed_request,
                mock_request_id,
                mock_background_tasks
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "State not found"

    @patch('app.controller.executed_state.State')
    async def test_executed_state_not_queued(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_executed_request,
        mock_background_tasks,
        mock_request_id
    ):
        """Test when state is not in QUEUED status"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.CREATED  # Not QUEUED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await executed_state(
                mock_namespace,
                mock_state_id,
                mock_executed_request,
                mock_request_id,
                mock_background_tasks
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is not queued"

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    async def test_executed_state_empty_outputs(
        self,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_background_tasks,
        mock_request_id
    ):
        """Test execution with empty outputs"""
        # Arrange
        executed_request = ExecutedRequestModel(outputs=[])
        
        # Mock State.find_one() for finding the state
        # Mock State.find_one().set() for updating the state
        mock_update_query = MagicMock()
        mock_update_query.set = AsyncMock()
        
        # Configure State.find_one to return different values based on call
        # First call returns the state object, second call returns a query object with set method
        mock_state_class.find_one = AsyncMock(return_value=mock_state)
        mock_state.save = AsyncMock()

        # Act
        result = await executed_state(
            mock_namespace,
            mock_state_id,
            executed_request,
            mock_request_id,
            mock_background_tasks
        )

        # Assert
        assert result.status == StateStatusEnum.EXECUTED
        assert mock_state.outputs == {}
        mock_background_tasks.add_task.assert_called_once_with(mock_create_next_states, [mock_state.id], mock_state.identifier, mock_state.namespace_name, mock_state.graph_name, mock_state.parents)

    @patch('app.controller.executed_state.State')
    async def test_executed_state_database_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_executed_request,
        mock_background_tasks,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_state_class.find_one = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await executed_state(
                mock_namespace,
                mock_state_id,
                mock_executed_request,
                mock_request_id,
                mock_background_tasks
            )
        
        assert str(exc_info.value) == "Database error"

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    async def test_executed_state_general_exception_handling(
        self,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_executed_request,
        mock_state,
        mock_background_tasks,
        mock_request_id
    ):
        """Test general exception handling in executed_state function"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=mock_state)
        mock_state.save = AsyncMock(side_effect=Exception("Save error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await executed_state(
                mock_namespace,
                mock_state_id,
                mock_executed_request,
                mock_request_id,
                mock_background_tasks
            )
        
        assert str(exc_info.value) == "Save error"

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    async def test_executed_state_state_id_none(
        self,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_executed_request,
        mock_background_tasks,
        mock_request_id
    ):
        """Test when state is found but has None ID"""
        # Arrange
        mock_state = MagicMock()
        mock_state.id = None
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await executed_state(
                mock_namespace,
                mock_state_id,
                mock_executed_request,
                mock_request_id,
                mock_background_tasks
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "State not found"

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    async def test_executed_state_insert_many_partial_failure(
        self,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_background_tasks,
        mock_request_id
    ):
        """Test when insert_many returns partial results (this is valid behavior)"""
        # Arrange
        executed_request = ExecutedRequestModel(
            outputs=[
                {"result": "success1"},
                {"result": "success2"},
                {"result": "success3"}
            ]
        )

        mock_state_class.find_one = AsyncMock(return_value=mock_state)
        mock_state.save = AsyncMock()
        
        # Mock partial insert - only 1 state inserted instead of 2 (this is valid)
        new_ids = [PydanticObjectId()]
        mock_state_class.insert_many = AsyncMock(return_value=MagicMock(inserted_ids=new_ids))
        mock_state_class.find = MagicMock(return_value=AsyncMock(to_list=AsyncMock(return_value=[mock_state])))

        # Act
        result = await executed_state(
            mock_namespace,
            mock_state_id,
            executed_request,
            mock_request_id,
            mock_background_tasks
        )

        # Assert - Should complete successfully with partial results
        assert result.status == StateStatusEnum.EXECUTED

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    async def test_executed_state_insert_many_complete_failure(
        self,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_background_tasks,
        mock_request_id
    ):
        """Test when insert_many returns no inserted states (this is valid behavior)"""
        # Arrange
        executed_request = ExecutedRequestModel(
            outputs=[
                {"result": "success1"},
                {"result": "success2"}
            ]
        )

        mock_state_class.find_one = AsyncMock(return_value=mock_state)
        mock_state.save = AsyncMock()
        
        # Mock complete insert failure - no states inserted (this is valid)
        mock_state_class.insert_many = AsyncMock(return_value=MagicMock(inserted_ids=[]))
        mock_state_class.find = MagicMock(return_value=AsyncMock(to_list=AsyncMock(return_value=[])))

        # Act
        result = await executed_state(
            mock_namespace,
            mock_state_id,
            executed_request,
            mock_request_id,
            mock_background_tasks
        )

        # Assert - Should complete successfully even with no new states
        assert result.status == StateStatusEnum.EXECUTED

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    @patch('app.controller.executed_state.logger')
    async def test_executed_state_logging_info_and_error(
        self,
        mock_logger,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_executed_request,
        mock_background_tasks,
        mock_request_id
    ):
        """Test that proper logging occurs during success and error scenarios"""
        # Arrange - Success scenario
        mock_state = MagicMock()
        mock_state.id = PydanticObjectId()
        mock_state.status = StateStatusEnum.QUEUED
        mock_state.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act - Success scenario
        await executed_state(
            mock_namespace,
            mock_state_id,
            mock_executed_request,
            mock_request_id,
            mock_background_tasks
        )

        # Assert - Success logging
        mock_logger.info.assert_called_once_with(
            f"Executed state {mock_state_id} for namespace {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

        # Arrange - Error scenario
        mock_logger.reset_mock()
        mock_state_class.find_one = AsyncMock(side_effect=Exception("Test error"))

        # Act - Error scenario
        with pytest.raises(Exception):
            await executed_state(
                mock_namespace,
                mock_state_id,
                mock_executed_request,
                mock_request_id,
                mock_background_tasks
            )

        # Assert - Error logging
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert f"Error executing state {mock_state_id} for namespace {mock_namespace}" in str(call_args)

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    async def test_executed_state_preserves_state_attributes_for_new_states(
        self,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_background_tasks,
        mock_request_id
    ):
        """Test that new states preserve all necessary attributes from the original state"""
        # Arrange
        executed_request = ExecutedRequestModel(
            outputs=[
                {"result": "success1"},
                {"result": "success2"}
            ]
        )

        # Set up specific state attributes
        mock_state.node_name = "test_node"
        mock_state.namespace_name = "test_namespace"
        mock_state.identifier = "test_identifier"
        mock_state.graph_name = "test_graph"
        mock_state.run_id = "test_run_id"
        mock_state.inputs = {"key": "value"}
        mock_state.parents = {"parent1": PydanticObjectId()}

        mock_state_class.find_one = AsyncMock(return_value=mock_state)
        mock_state.save = AsyncMock()
        
        new_ids = [PydanticObjectId()]
        mock_state_class.insert_many = AsyncMock(return_value=MagicMock(inserted_ids=new_ids))
        mock_state_class.find = MagicMock(return_value=AsyncMock(to_list=AsyncMock(return_value=[mock_state])))

        # Act
        await executed_state(
            mock_namespace,
            mock_state_id,
            executed_request,
            mock_request_id,
            mock_background_tasks
        )

        # Assert that State was called with correct parameters for new state creation
        state_call = mock_state_class.call_args
        assert state_call[1]['node_name'] == mock_state.node_name
        assert state_call[1]['namespace_name'] == mock_state.namespace_name
        assert state_call[1]['identifier'] == mock_state.identifier
        assert state_call[1]['graph_name'] == mock_state.graph_name
        assert state_call[1]['run_id'] == mock_state.run_id
        assert state_call[1]['inputs'] == mock_state.inputs
        assert state_call[1]['parents'] == mock_state.parents
        assert state_call[1]['status'] == StateStatusEnum.EXECUTED
        assert state_call[1]['outputs'] == {"result": "success2"}
        assert state_call[1]['error'] is None

    @patch('app.controller.executed_state.State')
    @patch('app.controller.executed_state.create_next_states')
    async def test_executed_state_all_status_transitions(
        self,
        mock_create_next_states,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state,
        mock_background_tasks,
        mock_request_id
    ):
        """Test all valid status transitions in executed_state"""
        # Test with QUEUED status (valid)
        mock_state.status = StateStatusEnum.QUEUED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)
        mock_state.save = AsyncMock()

        executed_request = ExecutedRequestModel(outputs=[{"result": "success"}])
        
        result = await executed_state(
            mock_namespace,
            mock_state_id,
            executed_request,
            mock_request_id,
            mock_background_tasks
        )

        assert result.status == StateStatusEnum.EXECUTED
        assert mock_state.status == StateStatusEnum.EXECUTED

        # Test with invalid statuses
        for invalid_status in [StateStatusEnum.CREATED, StateStatusEnum.EXECUTED, 
                              StateStatusEnum.SUCCESS, StateStatusEnum.ERRORED]:
            mock_state.status = invalid_status
            mock_state_class.find_one = AsyncMock(return_value=mock_state)
            
            with pytest.raises(HTTPException) as exc_info:
                await executed_state(
                    mock_namespace,
                    mock_state_id,
                    executed_request,
                    mock_request_id,
                    mock_background_tasks
                )
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == "State is not queued"

