import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.state_status_enum import StateStatusEnum


class TestCheckNodeTimeout:

    @pytest.mark.asyncio
    async def test_check_node_timeout_marks_timed_out_states(self):
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.modified_count = 3
        mock_collection.update_many = AsyncMock(return_value=mock_result)

        with patch('app.tasks.check_node_timeout.State') as mock_state, \
             patch('app.tasks.check_node_timeout.get_settings') as mock_get_settings:
            
            from app.tasks.check_node_timeout import check_node_timeout
            
            mock_settings = MagicMock()
            mock_settings.node_timeout_minutes = 30
            mock_get_settings.return_value = mock_settings

            mock_state.get_pymongo_collection.return_value = mock_collection

            await check_node_timeout()

            mock_collection.update_many.assert_called_once()
            call_args = mock_collection.update_many.call_args
            
            query = call_args[0][0]
            update = call_args[0][1]

            assert query["status"] == StateStatusEnum.QUEUED
            assert "$ne" in query["queued_at"]
            assert "$lte" in query["queued_at"]
            
            assert update["$set"]["status"] == StateStatusEnum.TIMEDOUT
            assert "timed out after 30 minutes" in update["$set"]["error"]

    @pytest.mark.asyncio
    async def test_check_node_timeout_no_timed_out_states(self):
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.modified_count = 0
        mock_collection.update_many = AsyncMock(return_value=mock_result)

        with patch('app.tasks.check_node_timeout.State') as mock_state, \
             patch('app.tasks.check_node_timeout.get_settings') as mock_get_settings:
            
            from app.tasks.check_node_timeout import check_node_timeout
            
            mock_settings = MagicMock()
            mock_settings.node_timeout_minutes = 30
            mock_get_settings.return_value = mock_settings

            mock_state.get_pymongo_collection.return_value = mock_collection

            await check_node_timeout()

            mock_collection.update_many.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_node_timeout_handles_exception(self):
        mock_collection = MagicMock()
        mock_collection.update_many = AsyncMock(side_effect=Exception("Database error"))

        with patch('app.tasks.check_node_timeout.State') as mock_state, \
             patch('app.tasks.check_node_timeout.get_settings') as mock_get_settings, \
             patch('app.tasks.check_node_timeout.logger') as mock_logger:
            
            from app.tasks.check_node_timeout import check_node_timeout
            
            mock_settings = MagicMock()
            mock_settings.node_timeout_minutes = 30
            mock_get_settings.return_value = mock_settings

            mock_state.get_pymongo_collection.return_value = mock_collection

            await check_node_timeout()

            mock_logger.error.assert_called_once()
            error_message = mock_logger.error.call_args[0][0]
            assert "Error checking node timeout" in error_message

    @pytest.mark.asyncio
    async def test_check_node_timeout_calculates_correct_threshold(self):
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.modified_count = 0
        mock_collection.update_many = AsyncMock(return_value=mock_result)

        with patch('app.tasks.check_node_timeout.State') as mock_state, \
             patch('app.tasks.check_node_timeout.get_settings') as mock_get_settings, \
             patch('app.tasks.check_node_timeout.time') as mock_time:
            
            from app.tasks.check_node_timeout import check_node_timeout
            
            mock_time.time.return_value = 1000
            
            mock_settings = MagicMock()
            mock_settings.node_timeout_minutes = 45
            mock_get_settings.return_value = mock_settings

            mock_state.get_pymongo_collection.return_value = mock_collection

            await check_node_timeout()

            call_args = mock_collection.update_many.call_args
            query = call_args[0][0]
            
            expected_threshold = (1000 * 1000) - (45 * 60 * 1000)
            assert query["queued_at"]["$lte"] == expected_threshold
