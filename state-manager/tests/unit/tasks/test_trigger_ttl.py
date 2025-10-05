"""
Tests for trigger TTL (Time To Live) expiration logic.
Verifies that completed/failed triggers are properly marked for cleanup.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta, timezone

from app.tasks.trigger_cron import mark_as_triggered, mark_as_failed, mark_as_cancelled
from app.models.db.trigger import DatabaseTriggers
from app.models.trigger_models import TriggerStatusEnum


@pytest.mark.asyncio
@pytest.mark.parametrize("mark_function,expected_status", [
    (mark_as_triggered, TriggerStatusEnum.TRIGGERED),
    (mark_as_failed, TriggerStatusEnum.FAILED),
    (mark_as_cancelled, TriggerStatusEnum.CANCELLED),
])
async def test_mark_trigger_sets_expires_at(mark_function, expected_status):
    """Test that marking a trigger sets the expires_at field correctly"""
    # Create a mock trigger
    trigger = MagicMock(spec=DatabaseTriggers)
    trigger.id = "test_trigger_id"

    # Mock the database update
    with patch.object(DatabaseTriggers, 'get_pymongo_collection') as mock_collection:
        mock_collection.return_value.update_one = AsyncMock()

        # Call the function with retention_days parameter
        await mark_function(trigger, retention_days=30)

        # Verify update_one was called
        assert mock_collection.return_value.update_one.called
        call_args = mock_collection.return_value.update_one.call_args

        # Verify the filter (first argument)
        assert call_args[0][0] == {"_id": trigger.id}

        # Verify the update includes both status and expires_at
        update_dict = call_args[0][1]["$set"]
        assert update_dict["trigger_status"] == expected_status
        assert "expires_at" in update_dict

        # Verify expires_at is approximately 30 days from now (UTC)
        expires_at = update_dict["expires_at"]
        expected_expiry = datetime.now(timezone.utc) + timedelta(days=30)
        time_diff = abs((expires_at - expected_expiry).total_seconds())
        assert time_diff < 2  # Within 2 seconds tolerance

        # Verify expires_at is timezone-aware UTC
        assert expires_at.tzinfo is not None
        assert expires_at.tzinfo == timezone.utc


@pytest.mark.asyncio
@pytest.mark.parametrize("mark_function,retention_days", [
    (mark_as_triggered, 7),
    (mark_as_failed, 14),
    (mark_as_cancelled, 21),
])
async def test_mark_trigger_uses_custom_retention_period(mark_function, retention_days):
    """Test that custom retention period is respected"""
    # Create a mock trigger
    trigger = MagicMock(spec=DatabaseTriggers)
    trigger.id = "test_trigger_id"

    # Mock the database update
    with patch.object(DatabaseTriggers, 'get_pymongo_collection') as mock_collection:
        mock_collection.return_value.update_one = AsyncMock()

        # Call the function with custom retention period
        await mark_function(trigger, retention_days=retention_days)

        # Verify expires_at is approximately retention_days from now (UTC)
        call_args = mock_collection.return_value.update_one.call_args
        update_dict = call_args[0][1]["$set"]
        expires_at = update_dict["expires_at"]
        expected_expiry = datetime.now(timezone.utc) + timedelta(days=retention_days)
        time_diff = abs((expires_at - expected_expiry).total_seconds())
        assert time_diff < 2  # Within 2 seconds tolerance

        # Verify expires_at is timezone-aware UTC
        assert expires_at.tzinfo is not None
        assert expires_at.tzinfo == timezone.utc