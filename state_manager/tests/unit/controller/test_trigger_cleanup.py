# Path: tests/unit/controller/test_trigger_cleanup.py

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta, timezone

from app.controller.trigger_cleanup import cleanup_old_triggers
from app.models.trigger_models import TriggerStatusEnum


@pytest.mark.asyncio
@patch("app.controller.trigger_cleanup.DatabaseTriggers.get_pymongo_collection")
async def test_cleanup_old_triggers(mock_get_collection):
    """
    Test cleanup_old_triggers() deletes only old CANCELLED or TRIGGERED triggers.
    """
    # Setup mock collection
    mock_delete_result = AsyncMock()
    mock_delete_result.deleted_count = 2
    mock_collection = AsyncMock()
    mock_collection.delete_many.return_value = mock_delete_result      
    mock_get_collection.return_value = mock_collection

    # Call cleanup
    await cleanup_old_triggers()

    # Assert delete_many called with correct query
    mock_collection.delete_many.assert_called_once()
    args, kwargs = mock_collection.delete_many.call_args
    query = args[0]

    # Check trigger_status filter
    assert query["trigger_status"]["$in"] == [TriggerStatusEnum.CANCELLED, TriggerStatusEnum.TRIGGERED]

    # Check trigger_time filter exists and is datetime
    assert "$lte" in query["trigger_time"]
    cutoff_time = query["trigger_time"]["$lte"]
    assert isinstance(cutoff_time, datetime)
    assert cutoff_time.tzinfo is not None  # ensure UTC-aware

    # Optional: Ensure cutoff is in the past
    assert cutoff_time <= datetime.now(timezone.utc)
