import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.controller.manual_retry_state import manual_retry_state
from app.models.manual_retry import ManualRetryRequestModel, ManualRetryResponseModel
from app.models.state_status_enum import StateStatusEnum


class TestManualRetryState:
    """Test cases for manual_retry_state function"""

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
    def mock_manual_retry_request(self):
        return ManualRetryRequestModel(
            fanout_id="test-fanout-id-123"
        )

    @pytest.fixture
    def mock_original_state(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.node_name = "test_node"
        state.namespace_name = "test_namespace"
        state.identifier = "test_identifier"
        state.graph_name = "test_graph"
        state.run_id = "test_run_id"
        state.status = StateStatusEnum.EXECUTED
        state.inputs = {"key": "value"}
        state.outputs = {"result": "success"}
        state.error = "Original error"
        state.parents = {"parent1": PydanticObjectId()}
        state.does_unites = False
        state.save = AsyncMock()
        return state

    @pytest.fixture
    def mock_retry_state(self):
        retry_state = MagicMock()
        retry_state.id = PydanticObjectId()
        retry_state.status = StateStatusEnum.CREATED
        retry_state.insert = AsyncMock(return_value=retry_state)
        return retry_state

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_success(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_original_state,
        mock_retry_state,
        mock_request_id
    ):
        """Test successful manual retry state creation"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=mock_original_state)
        mock_state_class.return_value = mock_retry_state

        # Act
        result = await manual_retry_state(
            mock_namespace,
            mock_state_id,
            mock_manual_retry_request,
            mock_request_id
        )

        # Assert
        assert isinstance(result, ManualRetryResponseModel)
        assert result.id == str(mock_retry_state.id)
        assert result.status == StateStatusEnum.CREATED

        # Verify State.find_one was called with correct parameters
        mock_state_class.find_one.assert_called_once()
        call_args = mock_state_class.find_one.call_args[0]
        # Check that both conditions were passed
        assert len(call_args) == 2

        # Verify original state was updated to RETRY_CREATED
        assert mock_original_state.status == StateStatusEnum.RETRY_CREATED
        mock_original_state.save.assert_called_once()

        # Verify retry state was created with correct attributes
        mock_state_class.assert_called_once()
        retry_state_args = mock_state_class.call_args[1]
        assert retry_state_args['node_name'] == mock_original_state.node_name
        assert retry_state_args['namespace_name'] == mock_original_state.namespace_name
        assert retry_state_args['identifier'] == mock_original_state.identifier
        assert retry_state_args['graph_name'] == mock_original_state.graph_name
        assert retry_state_args['run_id'] == mock_original_state.run_id
        assert retry_state_args['status'] == StateStatusEnum.CREATED
        assert retry_state_args['inputs'] == mock_original_state.inputs
        assert retry_state_args['outputs'] == {}
        assert retry_state_args['error'] is None
        assert retry_state_args['parents'] == mock_original_state.parents
        assert retry_state_args['does_unites'] == mock_original_state.does_unites
        assert retry_state_args['fanout_id'] == mock_manual_retry_request.fanout_id

        # Verify retry state was inserted
        mock_retry_state.insert.assert_called_once()

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_not_found(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_request_id
    ):
        """Test when original state is not found"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await manual_retry_state(
                mock_namespace,
                mock_state_id,
                mock_manual_retry_request,
                mock_request_id
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "State not found"

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_duplicate_key_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_original_state,
        mock_retry_state,
        mock_request_id
    ):
        """Test when duplicate retry state is detected"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=mock_original_state)
        mock_retry_state.insert = AsyncMock(side_effect=DuplicateKeyError("Duplicate key"))
        mock_state_class.return_value = mock_retry_state

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await manual_retry_state(
                mock_namespace,
                mock_state_id,
                mock_manual_retry_request,
                mock_request_id
            )

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert exc_info.value.detail == "Duplicate retry state detected"

        # Verify original state was not updated since duplicate was detected
        mock_original_state.save.assert_not_called()

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_with_different_fanout_id(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_original_state,
        mock_retry_state,
        mock_request_id
    ):
        """Test manual retry with different fanout_id"""
        # Arrange
        different_fanout_request = ManualRetryRequestModel(
            fanout_id="different-fanout-id-456"
        )
        mock_state_class.find_one = AsyncMock(return_value=mock_original_state)
        mock_state_class.return_value = mock_retry_state

        # Act
        result = await manual_retry_state(
            mock_namespace,
            mock_state_id,
            different_fanout_request,
            mock_request_id
        )

        # Assert
        assert isinstance(result, ManualRetryResponseModel)
        assert result.id == str(mock_retry_state.id)
        assert result.status == StateStatusEnum.CREATED

        # Verify retry state was created with the different fanout_id
        retry_state_args = mock_state_class.call_args[1]
        assert retry_state_args['fanout_id'] == "different-fanout-id-456"

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_with_complex_inputs_and_parents(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_retry_state,
        mock_request_id
    ):
        """Test manual retry with complex inputs and multiple parents"""
        # Arrange
        complex_state = MagicMock()
        complex_state.id = PydanticObjectId()
        complex_state.node_name = "complex_node"
        complex_state.namespace_name = "test_namespace"
        complex_state.identifier = "complex_identifier"
        complex_state.graph_name = "complex_graph"
        complex_state.run_id = "complex_run_id"
        complex_state.status = StateStatusEnum.ERRORED
        complex_state.inputs = {
            "nested_data": {"key1": "value1", "key2": [1, 2, 3]},
            "simple_value": "test",
            "number": 42
        }
        complex_state.outputs = {"previous_result": "some_output"}
        complex_state.error = "Complex error message"
        complex_state.parents = {
            "parent1": PydanticObjectId(),
            "parent2": PydanticObjectId(),
            "parent3": PydanticObjectId()
        }
        complex_state.does_unites = True
        complex_state.save = AsyncMock()

        mock_state_class.find_one = AsyncMock(return_value=complex_state)
        mock_state_class.return_value = mock_retry_state

        # Act
        result = await manual_retry_state(
            mock_namespace,
            mock_state_id,
            mock_manual_retry_request,
            mock_request_id
        )

        # Assert
        assert isinstance(result, ManualRetryResponseModel)

        # Verify retry state preserves complex data structures
        retry_state_args = mock_state_class.call_args[1]
        assert retry_state_args['inputs'] == complex_state.inputs
        assert retry_state_args['parents'] == complex_state.parents
        assert retry_state_args['does_unites'] == complex_state.does_unites
        assert retry_state_args['outputs'] == {}  # Should be reset
        assert retry_state_args['error'] is None  # Should be reset

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_database_error_on_find(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_request_id
    ):
        """Test handling of database error during state lookup"""
        # Arrange
        mock_state_class.find_one = AsyncMock(side_effect=Exception("Database connection error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await manual_retry_state(
                mock_namespace,
                mock_state_id,
                mock_manual_retry_request,
                mock_request_id
            )

        assert str(exc_info.value) == "Database connection error"

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_database_error_on_save(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_original_state,
        mock_retry_state,
        mock_request_id
    ):
        """Test handling of database error during original state save"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=mock_original_state)
        mock_state_class.return_value = mock_retry_state
        mock_original_state.save = AsyncMock(side_effect=Exception("Save operation failed"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await manual_retry_state(
                mock_namespace,
                mock_state_id,
                mock_manual_retry_request,
                mock_request_id
            )

        assert str(exc_info.value) == "Save operation failed"

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_database_error_on_insert(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_original_state,
        mock_retry_state,
        mock_request_id
    ):
        """Test handling of database error during retry state insert (non-duplicate)"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=mock_original_state)
        mock_retry_state.insert = AsyncMock(side_effect=Exception("Insert operation failed"))
        mock_state_class.return_value = mock_retry_state

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await manual_retry_state(
                mock_namespace,
                mock_state_id,
                mock_manual_retry_request,
                mock_request_id
            )

        assert str(exc_info.value) == "Insert operation failed"

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_empty_inputs_and_parents(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_retry_state,
        mock_request_id
    ):
        """Test manual retry with empty inputs and parents"""
        # Arrange
        empty_state = MagicMock()
        empty_state.id = PydanticObjectId()
        empty_state.node_name = "empty_node"
        empty_state.namespace_name = "test_namespace"
        empty_state.identifier = "empty_identifier"
        empty_state.graph_name = "empty_graph"
        empty_state.run_id = "empty_run_id"
        empty_state.status = StateStatusEnum.EXECUTED
        empty_state.inputs = {}
        empty_state.outputs = {}
        empty_state.error = None
        empty_state.parents = {}
        empty_state.does_unites = False
        empty_state.save = AsyncMock()

        mock_state_class.find_one = AsyncMock(return_value=empty_state)
        mock_state_class.return_value = mock_retry_state

        # Act
        result = await manual_retry_state(
            mock_namespace,
            mock_state_id,
            mock_manual_retry_request,
            mock_request_id
        )

        # Assert
        assert isinstance(result, ManualRetryResponseModel)

        # Verify retry state handles empty collections correctly
        retry_state_args = mock_state_class.call_args[1]
        assert retry_state_args['inputs'] == {}
        assert retry_state_args['parents'] == {}
        assert retry_state_args['outputs'] == {}
        assert retry_state_args['error'] is None

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_namespace_mismatch(
        self,
        mock_state_class,
        mock_state_id,
        mock_manual_retry_request,
        mock_request_id
    ):
        """Test manual retry with namespace that doesn't match any state"""
        # Arrange
        different_namespace = "different_namespace"
        mock_state_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await manual_retry_state(
                different_namespace,
                mock_state_id,
                mock_manual_retry_request,
                mock_request_id
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "State not found"

        # Verify find_one was called with the different namespace
        mock_state_class.find_one.assert_called_once()

    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_preserves_all_original_fields(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_retry_state,
        mock_request_id
    ):
        """Test that all relevant fields from original state are preserved in retry state"""
        # Arrange
        original_state = MagicMock()
        original_state.id = PydanticObjectId()
        original_state.node_name = "preserve_test_node"
        original_state.namespace_name = "preserve_test_namespace"
        original_state.identifier = "preserve_test_identifier"
        original_state.graph_name = "preserve_test_graph"
        original_state.run_id = "preserve_test_run_id"
        original_state.status = StateStatusEnum.EXECUTED
        original_state.inputs = {"preserve": "input_data"}
        original_state.outputs = {"should_be": "reset"}
        original_state.error = "should_be_reset"
        original_state.parents = {"preserve_parent": PydanticObjectId()}
        original_state.does_unites = True
        original_state.save = AsyncMock()

        mock_state_class.find_one = AsyncMock(return_value=original_state)
        mock_state_class.return_value = mock_retry_state

        # Act
        await manual_retry_state(
            mock_namespace,
            mock_state_id,
            mock_manual_retry_request,
            mock_request_id
        )

        # Assert - verify all fields are correctly set
        retry_state_args = mock_state_class.call_args[1]
        
        # Fields that should be preserved
        assert retry_state_args['node_name'] == original_state.node_name
        assert retry_state_args['namespace_name'] == original_state.namespace_name
        assert retry_state_args['identifier'] == original_state.identifier
        assert retry_state_args['graph_name'] == original_state.graph_name
        assert retry_state_args['run_id'] == original_state.run_id
        assert retry_state_args['inputs'] == original_state.inputs
        assert retry_state_args['parents'] == original_state.parents
        assert retry_state_args['does_unites'] == original_state.does_unites
        assert retry_state_args['fanout_id'] == mock_manual_retry_request.fanout_id
        
        # Fields that should be reset/set to specific values
        assert retry_state_args['status'] == StateStatusEnum.CREATED
        assert retry_state_args['outputs'] == {}
        assert retry_state_args['error'] is None

    @patch('app.controller.manual_retry_state.logger')
    @patch('app.controller.manual_retry_state.State')
    async def test_manual_retry_state_logging_calls(
        self,
        mock_state_class,
        mock_logger,
        mock_namespace,
        mock_state_id,
        mock_manual_retry_request,
        mock_original_state,
        mock_retry_state,
        mock_request_id
    ):
        """Test that appropriate logging calls are made"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=mock_original_state)
        mock_state_class.return_value = mock_retry_state

        # Act
        await manual_retry_state(
            mock_namespace,
            mock_state_id,
            mock_manual_retry_request,
            mock_request_id
        )

        # Assert - verify logging calls were made
        assert mock_logger.info.call_count >= 2  # At least initial log and success log
        
        # Check that the initial log contains expected information
        first_call_args = mock_logger.info.call_args_list[0]
        assert str(mock_state_id) in first_call_args[0][0]
        assert mock_namespace in first_call_args[0][0]
        assert first_call_args[1]['x_exosphere_request_id'] == mock_request_id
        
        # Check that the success log contains retry state id
        second_call_args = mock_logger.info.call_args_list[1]
        assert str(mock_retry_state.id) in second_call_args[0][0]
        assert str(mock_state_id) in second_call_args[0][0]
        assert second_call_args[1]['x_exosphere_request_id'] == mock_request_id
