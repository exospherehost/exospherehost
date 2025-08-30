import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from app.controller.prune_signal import prune_signal
from app.models.signal_models import PruneRequestModel, SignalResponseModel
from app.models.state_status_enum import StateStatusEnum


class TestPruneSignal:
    """Test cases for prune_signal function"""

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
    def mock_prune_request(self):
        return PruneRequestModel(
            data={"key": "value", "nested": {"data": "test"}}
        )

    @pytest.fixture
    def mock_state_created(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.status = StateStatusEnum.CREATED
        state.enqueue_after = 1234567890
        return state

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_success(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_prune_request,
        mock_state_created,
        mock_request_id
    ):
        """Test successful pruning of state"""
        # Arrange
        mock_state_created.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_created)

        # Act
        result = await prune_signal(
            mock_namespace,
            mock_state_id,
            mock_prune_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.PRUNED
        assert result.enqueue_after == 1234567890
        assert mock_state_created.status == StateStatusEnum.PRUNED
        assert mock_state_created.data == mock_prune_request.data
        assert mock_state_created.save.call_count == 1
        assert mock_state_class.find_one.call_count == 1

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_state_not_found(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_prune_request,
        mock_request_id
    ):
        """Test when state is not found"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await prune_signal(
                mock_namespace,
                mock_state_id,
                mock_prune_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "State not found"

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_invalid_status_queued(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_prune_request,
        mock_request_id
    ):
        """Test when state is in QUEUED status (invalid for pruning)"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.QUEUED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await prune_signal(
                mock_namespace,
                mock_state_id,
                mock_prune_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is not created"

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_invalid_status_executed(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_prune_request,
        mock_request_id
    ):
        """Test when state is in EXECUTED status (invalid for pruning)"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.EXECUTED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await prune_signal(
                mock_namespace,
                mock_state_id,
                mock_prune_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is not created"

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_invalid_status_errored(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_prune_request,
        mock_request_id
    ):
        """Test when state is in ERRORED status (invalid for pruning)"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.ERRORED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await prune_signal(
                mock_namespace,
                mock_state_id,
                mock_prune_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is not created"

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_invalid_status_pruned(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_prune_request,
        mock_request_id
    ):
        """Test when state is already in PRUNED status (invalid for pruning)"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.PRUNED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await prune_signal(
                mock_namespace,
                mock_state_id,
                mock_prune_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is not created"

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_database_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_prune_request,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_state_class.find_one = MagicMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await prune_signal(
                mock_namespace,
                mock_state_id,
                mock_prune_request,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Database error"

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_save_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_prune_request,
        mock_state_created,
        mock_request_id
    ):
        """Test handling of save errors"""
        # Arrange
        mock_state_created.save = AsyncMock(side_effect=Exception("Save error"))
        mock_state_class.find_one = AsyncMock(return_value=mock_state_created)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await prune_signal(
                mock_namespace,
                mock_state_id,
                mock_prune_request,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Save error"

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_with_empty_data(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state_created,
        mock_request_id
    ):
        """Test pruning with empty data"""
        # Arrange
        prune_request = PruneRequestModel(data={})
        mock_state_created.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_created)

        # Act
        result = await prune_signal(
            mock_namespace,
            mock_state_id,
            prune_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.PRUNED
        assert mock_state_created.data == {}
        assert mock_state_created.save.call_count == 1

    @patch('app.controller.prune_signal.State')
    async def test_prune_signal_with_complex_data(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state_created,
        mock_request_id
    ):
        """Test pruning with complex nested data"""
        # Arrange
        complex_data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
            "nested": {
                "object": {
                    "deep": "value"
                }
            }
        }
        prune_request = PruneRequestModel(data=complex_data)
        mock_state_created.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_created)

        # Act
        result = await prune_signal(
            mock_namespace,
            mock_state_id,
            prune_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.PRUNED
        assert mock_state_created.data == complex_data
        assert mock_state_created.save.call_count == 1 