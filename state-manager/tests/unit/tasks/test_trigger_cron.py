"""
Tests for trigger_cron functions to improve code coverage.
These are pure unit tests that mock database operations.
Environment variables are provided by CI (see .github/workflows/test-state-manager.yml).
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from app.tasks.trigger_cron import create_next_triggers


@pytest.mark.asyncio
async def test_create_next_triggers_with_america_new_york_timezone():
    """Test create_next_triggers processes America/New_York timezone correctly"""
    trigger = MagicMock()
    trigger.expression = "0 9 * * *"
    trigger.timezone = "America/New_York"
    trigger.trigger_time = datetime(2025, 10, 4, 13, 0, 0)  # Naive UTC time
    trigger.graph_name = "test_graph"
    trigger.namespace = "test_namespace"

    cron_time = datetime(2025, 10, 6, 0, 0, 0)

    with patch('app.tasks.trigger_cron.DatabaseTriggers') as mock_db_class:
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_db_class.return_value = mock_instance

        await create_next_triggers(trigger, cron_time)

        # Verify DatabaseTriggers was instantiated with timezone
        assert mock_db_class.called
        call_kwargs = mock_db_class.call_args[1]
        assert call_kwargs['timezone'] == "America/New_York"
        assert call_kwargs['expression'] == "0 9 * * *"


@pytest.mark.asyncio
async def test_create_next_triggers_with_utc_timezone():
    """Test create_next_triggers with UTC timezone"""
    trigger = MagicMock()
    trigger.expression = "0 9 * * *"
    trigger.timezone = "UTC"
    trigger.trigger_time = datetime(2025, 10, 4, 9, 0, 0)
    trigger.graph_name = "test_graph"
    trigger.namespace = "test_namespace"

    cron_time = datetime(2025, 10, 6, 0, 0, 0)

    with patch('app.tasks.trigger_cron.DatabaseTriggers') as mock_db_class:
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_db_class.return_value = mock_instance

        await create_next_triggers(trigger, cron_time)

        # Verify timezone was passed correctly
        call_kwargs = mock_db_class.call_args[1]
        assert call_kwargs['timezone'] == "UTC"


@pytest.mark.asyncio
async def test_create_next_triggers_with_none_timezone_defaults_to_utc():
    """Test create_next_triggers with None timezone defaults to UTC"""
    trigger = MagicMock()
    trigger.expression = "0 9 * * *"
    trigger.timezone = None
    trigger.trigger_time = datetime(2025, 10, 4, 9, 0, 0)
    trigger.graph_name = "test_graph"
    trigger.namespace = "test_namespace"

    cron_time = datetime(2025, 10, 6, 0, 0, 0)

    with patch('app.tasks.trigger_cron.DatabaseTriggers') as mock_db_class:
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_db_class.return_value = mock_instance

        await create_next_triggers(trigger, cron_time)

        # Verify None timezone is passed through (will default to UTC in ZoneInfo call)
        call_kwargs = mock_db_class.call_args[1]
        assert call_kwargs['timezone'] is None


@pytest.mark.asyncio
async def test_create_next_triggers_with_europe_london_timezone():
    """Test create_next_triggers with Europe/London timezone"""
    trigger = MagicMock()
    trigger.expression = "0 17 * * *"
    trigger.timezone = "Europe/London"
    trigger.trigger_time = datetime(2025, 10, 4, 16, 0, 0)  # UTC time
    trigger.graph_name = "test_graph"
    trigger.namespace = "test_namespace"

    cron_time = datetime(2025, 10, 6, 0, 0, 0)

    with patch('app.tasks.trigger_cron.DatabaseTriggers') as mock_db_class:
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_db_class.return_value = mock_instance

        await create_next_triggers(trigger, cron_time)

        # Verify Europe/London timezone was used
        call_kwargs = mock_db_class.call_args[1]
        assert call_kwargs['timezone'] == "Europe/London"


@pytest.mark.asyncio
async def test_create_next_triggers_handles_duplicate_key_error():
    """Test create_next_triggers handles DuplicateKeyError gracefully"""
    from pymongo.errors import DuplicateKeyError

    trigger = MagicMock()
    trigger.expression = "0 9 * * *"
    trigger.timezone = "America/New_York"
    trigger.trigger_time = datetime(2025, 10, 4, 13, 0, 0)
    trigger.graph_name = "test_graph"
    trigger.namespace = "test_namespace"

    cron_time = datetime(2025, 10, 6, 0, 0, 0)

    with patch('app.tasks.trigger_cron.DatabaseTriggers') as mock_db_class:
        mock_instance = MagicMock()
        # First call raises DuplicateKeyError, second succeeds
        mock_instance.insert = AsyncMock(side_effect=[
            DuplicateKeyError("Duplicate"),
            None
        ])
        mock_db_class.return_value = mock_instance

        with patch('app.tasks.trigger_cron.logger') as mock_logger:
            # Should not raise exception
            await create_next_triggers(trigger, cron_time)

            # Verify error was logged
            assert mock_logger.error.called
            error_msg = mock_logger.error.call_args[0][0]
            assert "Duplicate trigger found" in error_msg


@pytest.mark.asyncio
async def test_create_next_triggers_trigger_time_is_datetime():
    """Test that next trigger_time is a datetime object"""
    trigger = MagicMock()
    trigger.expression = "0 9 * * *"
    trigger.timezone = "America/New_York"
    trigger.trigger_time = datetime(2025, 10, 4, 13, 0, 0)
    trigger.graph_name = "test_graph"
    trigger.namespace = "test_namespace"

    cron_time = datetime(2025, 10, 6, 0, 0, 0)

    with patch('app.tasks.trigger_cron.DatabaseTriggers') as mock_db_class:
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_db_class.return_value = mock_instance

        await create_next_triggers(trigger, cron_time)

        # Verify trigger_time is a datetime
        call_kwargs = mock_db_class.call_args[1]
        assert isinstance(call_kwargs['trigger_time'], datetime)


@pytest.mark.asyncio
async def test_create_next_triggers_creates_multiple_triggers():
    """Test create_next_triggers creates multiple future triggers"""
    trigger = MagicMock()
    trigger.expression = "0 */6 * * *"  # Every 6 hours
    trigger.timezone = "UTC"
    trigger.trigger_time = datetime(2025, 10, 4, 0, 0, 0)
    trigger.graph_name = "test_graph"
    trigger.namespace = "test_namespace"

    cron_time = datetime(2025, 10, 5, 0, 0, 0)  # 24 hours later

    with patch('app.tasks.trigger_cron.DatabaseTriggers') as mock_db_class:
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_db_class.return_value = mock_instance

        await create_next_triggers(trigger, cron_time)

        # Should create multiple triggers (every 6 hours until past cron_time)
        assert mock_db_class.call_count >= 4  # At least 4 triggers in 24 hours