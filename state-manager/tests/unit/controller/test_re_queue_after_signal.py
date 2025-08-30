import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from app.controller.re_queue_after_signal import re_queue_after_signal
from app.models.signal_models import ReEnqueueAfterRequestModel, SignalResponseModel
from app.models.state_status_enum import StateStatusEnum


class TestReQueueAfterSignal:
    """Test cases for re_queue_after_signal function"""

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
    def mock_re_enqueue_request(self):
        return ReEnqueueAfterRequestModel(
            enqueue_after=5000  # 5 seconds in milliseconds
        )

    @pytest.fixture
    def mock_state_any_status(self):
        state = MagicMock()
        state.id = PydanticObjectId()
        state.status = StateStatusEnum.QUEUED  # Any status is valid for re-enqueue
        state.enqueue_after = 1234567890
        return state

    @patch('app.controller.re_queue_after_signal.State')
    @patch('app.controller.re_queue_after_signal.time')
    async def test_re_queue_after_signal_success(
        self,
        mock_time,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_re_enqueue_request,
        mock_state_any_status,
        mock_request_id
    ):
        """Test successful re-enqueuing of state"""
        # Arrange
        mock_time.time.return_value = 1000.0  # Mock current time
        mock_state_any_status.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_any_status)

        # Act
        result = await re_queue_after_signal(
            mock_namespace,
            mock_state_id,
            mock_re_enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.CREATED
        assert result.enqueue_after == 1005000  # 1000 * 1000 + 5000
        assert mock_state_any_status.status == StateStatusEnum.CREATED
        assert mock_state_any_status.enqueue_after == 1005000
        assert mock_state_any_status.save.call_count == 1
        assert mock_state_class.find_one.call_count == 1

    @patch('app.controller.re_queue_after_signal.State')
    async def test_re_queue_after_signal_state_not_found(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_re_enqueue_request,
        mock_request_id
    ):
        """Test when state is not found"""
        # Arrange
        mock_state_class.find_one = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await re_queue_after_signal(
                mock_namespace,
                mock_state_id,
                mock_re_enqueue_request,
                mock_request_id
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "State not found"

    @patch('app.controller.re_queue_after_signal.State')
    @patch('app.controller.re_queue_after_signal.time')
    async def test_re_queue_after_signal_with_zero_delay(
        self,
        mock_time,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state_any_status,
        mock_request_id
    ):
        """Test re-enqueuing with zero delay"""
        # Arrange
        mock_time.time.return_value = 1000.0
        re_enqueue_request = ReEnqueueAfterRequestModel(enqueue_after=0)
        mock_state_any_status.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_any_status)

        # Act
        result = await re_queue_after_signal(
            mock_namespace,
            mock_state_id,
            re_enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.CREATED
        assert result.enqueue_after == 1000000  # 1000 * 1000 + 0
        assert mock_state_any_status.enqueue_after == 1000000
        assert mock_state_any_status.save.call_count == 1

    @patch('app.controller.re_queue_after_signal.State')
    @patch('app.controller.re_queue_after_signal.time')
    async def test_re_queue_after_signal_with_large_delay(
        self,
        mock_time,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state_any_status,
        mock_request_id
    ):
        """Test re-enqueuing with large delay"""
        # Arrange
        mock_time.time.return_value = 1000.0
        re_enqueue_request = ReEnqueueAfterRequestModel(enqueue_after=86400000)  # 24 hours
        mock_state_any_status.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_any_status)

        # Act
        result = await re_queue_after_signal(
            mock_namespace,
            mock_state_id,
            re_enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.CREATED
        assert result.enqueue_after == 87400000  # 1000 * 1000 + 86400000
        assert mock_state_any_status.enqueue_after == 87400000
        assert mock_state_any_status.save.call_count == 1

    @patch('app.controller.re_queue_after_signal.State')
    @patch('app.controller.re_queue_after_signal.time')
    async def test_re_queue_after_signal_with_negative_delay(
        self,
        mock_time,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_state_any_status,
        mock_request_id
    ):
        """Test re-enqueuing with negative delay (should still work)"""
        # Arrange
        mock_time.time.return_value = 1000.0
        re_enqueue_request = ReEnqueueAfterRequestModel(enqueue_after=-5000)  # Negative delay
        mock_state_any_status.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_any_status)

        # Act
        result = await re_queue_after_signal(
            mock_namespace,
            mock_state_id,
            re_enqueue_request,
            mock_request_id
        )

        # Assert
        assert result.status == StateStatusEnum.CREATED
        assert result.enqueue_after == 995000  # 1000 * 1000 + (-5000)
        assert mock_state_any_status.enqueue_after == 995000
        assert mock_state_any_status.save.call_count == 1

    @patch('app.controller.re_queue_after_signal.State')
    async def test_re_queue_after_signal_database_error(
        self,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_re_enqueue_request,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_state_class.find_one = MagicMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await re_queue_after_signal(
                mock_namespace,
                mock_state_id,
                mock_re_enqueue_request,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Database error"

    @patch('app.controller.re_queue_after_signal.State')
    @patch('app.controller.re_queue_after_signal.time')
    async def test_re_queue_after_signal_save_error(
        self,
        mock_time,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_re_enqueue_request,
        mock_state_any_status,
        mock_request_id
    ):
        """Test handling of save errors"""
        # Arrange
        mock_time.time.return_value = 1000.0
        mock_state_any_status.save = AsyncMock(side_effect=Exception("Save error"))
        mock_state_class.find_one = AsyncMock(return_value=mock_state_any_status)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await re_queue_after_signal(
                mock_namespace,
                mock_state_id,
                mock_re_enqueue_request,
                mock_request_id
            )
        
        assert str(exc_info.value) == "Save error"

    @patch('app.controller.re_queue_after_signal.State')
    @patch('app.controller.re_queue_after_signal.time')
    async def test_re_queue_after_signal_from_different_statuses(
        self,
        mock_time,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_re_enqueue_request,
        mock_request_id
    ):
        """Test re-enqueuing from different initial statuses"""
        # Arrange
        mock_time.time.return_value = 1000.0
        
        test_cases = [
            StateStatusEnum.CREATED,
            StateStatusEnum.QUEUED,
            StateStatusEnum.EXECUTED,
            StateStatusEnum.ERRORED,
            StateStatusEnum.CANCELLED,
            StateStatusEnum.SUCCESS,
            StateStatusEnum.NEXT_CREATED_ERROR,
            StateStatusEnum.PRUNED
        ]
        
        for initial_status in test_cases:
            # Arrange for this test case
            mock_state = MagicMock()
            mock_state.id = PydanticObjectId()
            mock_state.status = initial_status
            mock_state.save = AsyncMock()
            mock_state_class.find_one = AsyncMock(return_value=mock_state)

            # Act
            result = await re_queue_after_signal(
                mock_namespace,
                mock_state_id,
                mock_re_enqueue_request,
                mock_request_id
            )

            # Assert
            assert result.status == StateStatusEnum.CREATED
            assert mock_state.status == StateStatusEnum.CREATED
            assert mock_state.save.call_count == 1

    @patch('app.controller.re_queue_after_signal.State')
    @patch('app.controller.re_queue_after_signal.time')
    async def test_re_queue_after_signal_time_precision(
        self,
        mock_time,
        mock_state_class,
        mock_namespace,
        mock_state_id,
        mock_re_enqueue_request,
        mock_state_any_status,
        mock_request_id
    ):
        """Test that time calculation is precise"""
        # Arrange
        mock_time.time.return_value = 1234.567  # Test with fractional seconds
        mock_state_any_status.save = AsyncMock()
        mock_state_class.find_one = AsyncMock(return_value=mock_state_any_status)

        # Act
        result = await re_queue_after_signal(
            mock_namespace,
            mock_state_id,
            mock_re_enqueue_request,
            mock_request_id
        )

        # Assert
        expected_enqueue_after = int(1234.567 * 1000) + 5000
        assert result.enqueue_after == expected_enqueue_after
        assert mock_state_any_status.enqueue_after == expected_enqueue_after 