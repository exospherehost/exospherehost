import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from app.controller.errored_state import errored_state
from app.models.errored_models import ErroredRequestModel
from app.models.state_status_enum import StateStatusEnum


class TestErroredState:
    """Test cases for errored_state function"""

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
    def mock_errored_request(self):
        return ErroredRequestModel(
            error="Test error message"
        )

    @pytest.fixture
    def mock_state_queued(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.status = StateStatusEnum.QUEUED
        return state

    @pytest.fixture
    def mock_state_executed(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.status = StateStatusEnum.EXECUTED
        return state

    @patch('app.controller.errored_state.State')
    async def test_errored_state_success_queued(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_state_queued,
        mock_request_id
    ):
        """Test successful error marking of queued state"""      
        
        mock_state_queued.save = AsyncMock()     
        
        mock_state_queued.status = StateStatusEnum.QUEUED
        mock_state_queued.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_queued)

        # Act
        result = await errored_state(
            mock_namespace,
            mock_state_id,
            mock_errored_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.ERRORED
        assert mock_state_class.find_one.call_count == 1  # Called once for finding
        

    @patch('app.controller.errored_state.State')
    async def test_errored_state_success_executed(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_state_executed,
        mock_request_id
    ):
        """Test successful error marking of executed state"""
      
        mock_state_executed.save = AsyncMock() 

        mock_state_executed.status = StateStatusEnum.QUEUED
        mock_state_executed.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_executed)

        # Act
        result = await errored_state(
            mock_namespace,
            mock_state_id,
            mock_errored_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.ERRORED
        assert mock_state_class.find_one.call_count == 1  # Called once for finding
        

    @patch('app.controller.errored_state.State')
    async def test_errored_state_not_found(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test when state is not found"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "State not found"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_invalid_status_created(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test when state is in CREATED status (invalid for error marking)"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.CREATED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is not queued or executed"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_invalid_status_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test when state is already in ERRORED status"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.ERRORED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is not queued or executed"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_already_executed(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test when state is already executed (should not allow error marking)"""
        # Arrange
        mock_state = MagicMock()
        mock_state.status = StateStatusEnum.EXECUTED
        mock_state_class.find_one = AsyncMock(return_value=mock_state)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "State is already executed"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_database_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_errored_request,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_state_class.find_one = MagicMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await errored_state(
                mock_namespace,
                mock_state_id,
                mock_errored_request,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Database error"

    @patch('app.controller.errored_state.State')
    async def test_errored_state_with_different_error_message(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state_queued,
        mock_request_id
    ):
        """Test error marking with different error message"""
        # Arrange
        errored_request = ErroredRequestModel(
            error="Different error message"
        )       
        
        mock_state_queued.save = AsyncMock()

        mock_state_queued.status = StateStatusEnum.QUEUED
        mock_state_queued.set = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_queued)

        # Act
        result = await errored_state(
            mock_namespace,
            mock_state_id,
            errored_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.ERRORED
        assert mock_state_class.find_one.call_count == 1  # Called once for finding
        assert mock_state_queued.error == "Different error message"

