"""
Tests for trigger TTL (Time To Live) expiration logic.
Verifies that completed/failed triggers are properly marked for cleanup.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

from app.tasks.trigger_cron import mark_as_triggered, mark_as_failed
from app.models.db.trigger import DatabaseTriggers
from app.models.trigger_models import TriggerStatusEnum


@pytest.mark.asyncio
async def test_mark_as_triggered_sets_expires_at():
    """Test that marking a trigger as TRIGGERED sets the expires_at field"""
    # Create a mock trigger
    trigger = MagicMock(spec=DatabaseTriggers)
    trigger.id = "test_trigger_id"

    # Mock the settings to return 30 days retention
    with patch('app.tasks.trigger_cron.get_settings') as mock_settings:
        mock_settings.return_value.trigger_retention_days = 30

        # Mock the database update
        with patch.object(DatabaseTriggers, 'get_pymongo_collection') as mock_collection:
            mock_collection.return_value.update_one = AsyncMock()

            # Call the function
            await mark_as_triggered(trigger)

            # Verify update_one was called
            assert mock_collection.return_value.update_one.called
            call_args = mock_collection.return_value.update_one.call_args

            # Verify the filter (first argument)
            assert call_args[0][0] == {"_id": trigger.id}

            # Verify the update includes both status and expires_at
            update_dict = call_args[0][1]["$set"]
            assert update_dict["trigger_status"] == TriggerStatusEnum.TRIGGERED
            assert "expires_at" in update_dict

            # Verify expires_at is approximately 30 days from now
            expires_at = update_dict["expires_at"]
            expected_expiry = datetime.now() + timedelta(days=30)
            time_diff = abs((expires_at - expected_expiry).total_seconds())
            assert time_diff < 2  # Within 2 seconds tolerance


@pytest.mark.asyncio
async def test_mark_as_failed_sets_expires_at():
    """Test that marking a trigger as FAILED sets the expires_at field"""
    # Create a mock trigger
    trigger = MagicMock(spec=DatabaseTriggers)
    trigger.id = "test_trigger_id"

    # Mock the settings to return 30 days retention
    with patch('app.tasks.trigger_cron.get_settings') as mock_settings:
        mock_settings.return_value.trigger_retention_days = 30

        # Mock the database update
        with patch.object(DatabaseTriggers, 'get_pymongo_collection') as mock_collection:
            mock_collection.return_value.update_one = AsyncMock()

            # Call the function
            await mark_as_failed(trigger)

            # Verify update_one was called
            assert mock_collection.return_value.update_one.called
            call_args = mock_collection.return_value.update_one.call_args

            # Verify the filter (first argument)
            assert call_args[0][0] == {"_id": trigger.id}

            # Verify the update includes both status and expires_at
            update_dict = call_args[0][1]["$set"]
            assert update_dict["trigger_status"] == TriggerStatusEnum.FAILED
            assert "expires_at" in update_dict

            # Verify expires_at is approximately 30 days from now
            expires_at = update_dict["expires_at"]
            expected_expiry = datetime.now() + timedelta(days=30)
            time_diff = abs((expires_at - expected_expiry).total_seconds())
            assert time_diff < 2  # Within 2 seconds tolerance


@pytest.mark.asyncio
async def test_mark_as_triggered_uses_custom_retention_period():
    """Test that custom retention period from settings is respected"""
    # Create a mock trigger
    trigger = MagicMock(spec=DatabaseTriggers)
    trigger.id = "test_trigger_id"

    # Mock the settings to return 7 days retention
    with patch('app.tasks.trigger_cron.get_settings') as mock_settings:
        mock_settings.return_value.trigger_retention_days = 7

        # Mock the database update
        with patch.object(DatabaseTriggers, 'get_pymongo_collection') as mock_collection:
            mock_collection.return_value.update_one = AsyncMock()

            # Call the function
            await mark_as_triggered(trigger)

            # Verify expires_at is approximately 7 days from now
            call_args = mock_collection.return_value.update_one.call_args
            update_dict = call_args[0][1]["$set"]
            expires_at = update_dict["expires_at"]
            expected_expiry = datetime.now() + timedelta(days=7)
            time_diff = abs((expires_at - expected_expiry).total_seconds())
            assert time_diff < 2  # Within 2 seconds tolerance


@pytest.mark.asyncio
async def test_mark_as_failed_uses_custom_retention_period():
    """Test that custom retention period from settings is respected for failed triggers"""
    # Create a mock trigger
    trigger = MagicMock(spec=DatabaseTriggers)
    trigger.id = "test_trigger_id"

    # Mock the settings to return 14 days retention
    with patch('app.tasks.trigger_cron.get_settings') as mock_settings:
        mock_settings.return_value.trigger_retention_days = 14

        # Mock the database update
        with patch.object(DatabaseTriggers, 'get_pymongo_collection') as mock_collection:
            mock_collection.return_value.update_one = AsyncMock()

            # Call the function
            await mark_as_failed(trigger)

            # Verify expires_at is approximately 14 days from now
            call_args = mock_collection.return_value.update_one.call_args
            update_dict = call_args[0][1]["$set"]
            expires_at = update_dict["expires_at"]
            expected_expiry = datetime.now() + timedelta(days=14)
            time_diff = abs((expires_at - expected_expiry).total_seconds())
            assert time_diff < 2  # Within 2 seconds tolerance