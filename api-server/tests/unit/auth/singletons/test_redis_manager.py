import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys

# Ensure the application's root directory is in the Python path to allow for absolute imports.
# This makes the test suite independent of the directory it's run from.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from app.singletons.RedisOperation import RedisOperation
from redis.exceptions import RedisError, ConnectionError, TimeoutError
from app.singletons.redis_manager import RedisManager


class TestRedisManager(unittest.TestCase):
    """
    A comprehensive, from-scratch test suite for the RedisManager singleton.

    This suite ensures that every component of the RedisManager is tested in isolation,
    with a robust setup and teardown process to handle the singleton pattern correctly.
    """

    def setUp(self):
        """
        Set up a clean, controlled environment before each test.

        This method patches all external dependencies to ensure tests are fast and reliable.
        """
        # Reset the singleton's instance cache before each test. This is the most
        # critical step for ensuring test isolation.
        if hasattr(RedisManager, '__closure__') and RedisManager.__closure__:
            for cell in RedisManager.__closure__:
                if isinstance(cell.cell_contents, dict):
                    cell.cell_contents.clear()
                    break

        # --- Mock Dependencies ---
        # We use patchers here to manage starting and stopping the patches cleanly.
        self.logs_patcher = patch('app.singletons.redis_manager.LogsManager')
        self.redis_patcher = patch('app.singletons.redis_manager.redis.Redis')
        self.sleep_patcher = patch('time.sleep')

        self.mock_logs_manager_class = self.logs_patcher.start()
        self.mock_redis_class = self.redis_patcher.start()
        self.mock_sleep = self.sleep_patcher.start()

        # Configure the mocks that were just created.
        self.mock_redis_client = MagicMock()

        # By default, we make the ping successful so RedisManager initializes without error.
        self.mock_redis_client.ping.return_value = True
        self.mock_redis_class.return_value = self.mock_redis_client

        self.mock_logger = MagicMock()
        self.mock_logs_manager_class.return_value.get_logger.return_value = self.mock_logger

    def tearDown(self):
        """
        Clean up the environment after each test by stopping all patchers.
        """
        patch.stopall()

    def test_initialization_with_custom_env_vars(self):
        """
        Verify that RedisManager correctly initializes using environment variables.
        """
        env_vars = {
            'REDIS_HOST': 'env-host',
            'REDIS_PORT': '9999',
            'REDIS_PASSWORD': 'env-password',
            'REDIS_DB': '10',
            'REDIS_MAX_RETRIES': '5',
            'REDIS_RETRY_DELAY': '2.5'
        }
        with patch.dict(os.environ, env_vars):
            # We reset the mock just before creating the instance to have a clean slate for our assertion.
            self.mock_redis_client.ping.reset_mock()
            manager = RedisManager()

            # Verify that the redis client was instantiated with the correct config.
            self.mock_redis_class.assert_called_once_with(
                host='env-host',
                port=9999,
                password='env-password',
                db=10,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )

            # Verify that the manager's internal config is set correctly.
            self.assertEqual(manager.max_retries, 5)
            self.assertEqual(manager.retry_delay, 2.5)

            # Verify that the connection was validated via a ping call during initialization.
            self.mock_redis_client.ping.assert_called_once()

    def test_get_client_returns_instance(self):
        """
        Verify that get_client() returns the underlying Redis client instance.
        """
        manager = RedisManager()
        client = manager.get_client()
        self.assertEqual(client, self.mock_redis_client)

    def test_validate_connection_success_on_first_try(self):
        """
        Verify _validate_connection returns True on immediate success.
        """
        manager = RedisManager()
        # Reset mock from the call made in __init__ to test the method in isolation.
        self.mock_redis_client.ping.reset_mock()

        # Manually call the real method and check its behavior.
        result = manager._validate_connection()

        self.assertTrue(result)
        self.mock_redis_client.ping.assert_called_once()
        self.mock_sleep.assert_not_called()

    def test_validate_connection_succeeds_after_retries(self):
        """
        Verify _validate_connection retries on failure and eventually succeeds.
        """
        manager = RedisManager()
        self.mock_redis_client.ping.reset_mock()  # Reset from __init__ call.

        # Simulate two failures, then a success.
        self.mock_redis_client.ping.side_effect = [ConnectionError, ConnectionError, True]

        result = manager._validate_connection()

        self.assertTrue(result)
        self.assertEqual(self.mock_redis_client.ping.call_count, 3)
        self.mock_sleep.assert_has_calls([call(manager.retry_delay), call(manager.retry_delay)])

    def test_validate_connection_fails_after_all_retries(self):
        """
        Verify _validate_connection returns False if all attempts fail.
        """
        manager = RedisManager()
        self.mock_redis_client.ping.reset_mock()  # Reset from __init__ call.

        manager.max_retries = 3  # Explicitly set for clarity
        self.mock_redis_client.ping.side_effect = ConnectionError("Connection failed")

        result = manager._validate_connection()

        self.assertFalse(result)
        self.assertEqual(self.mock_redis_client.ping.call_count, 3)
        self.mock_logger.error.assert_called_with("All Redis connection attempts failed")

    def test_execute_with_retry_raises_error_after_failures(self):
        """
        Verify _execute_with_retry raises RedisError after all retries fail.
        """
        manager = RedisManager()
        manager.max_retries = 2
        self.mock_redis_client.get.side_effect = TimeoutError("Timed out")

        with self.assertRaises(RedisError):
            manager._execute_with_retry(RedisOperation.GET, "some-key")

        self.assertEqual(self.mock_redis_client.get.call_count, 2)
        self.mock_logger.error.assert_called_with(
            "Redis operation failed after retries", operation=RedisOperation.GET
        )

    # --- Tests for Public Methods (these rely on the mocked _execute_with_retry) ---

    def test_set_with_ttl_success(self):
        """Test set_with_ttl succeeds by calling _execute_with_retry."""
        manager = RedisManager()
        with patch.object(manager, '_execute_with_retry') as mock_execute:
            manager.set_with_ttl("my-key", "my-value", 3600)
            mock_execute.assert_called_once_with(RedisOperation.SET, "my-key", "my-value", ex=3600)

    def test_set_with_ttl_failure_logs_error(self):
        """Test set_with_ttl returns False and logs an error on failure."""
        manager = RedisManager()
        with patch.object(manager, '_execute_with_retry', side_effect=RedisError("Set failed")):
            result = manager.set_with_ttl("my-key", "my-value", 3600)

            self.assertFalse(result)
            self.mock_logger.error.assert_called_once_with(
                "Failed to set key with TTL",
                key="my-key",
                ttl_seconds=3600,
                error="Set failed"
            )

    def test_exists_returns_true_when_key_present(self):
        """Test exists() returns True when _execute_with_retry returns > 0."""
        manager = RedisManager()
        with patch.object(manager, '_execute_with_retry', return_value=1) as mock_execute:
            self.assertTrue(manager.exists("my-key"))
            mock_execute.assert_called_once_with(RedisOperation.EXISTS, "my-key")

    def test_get_returns_value_on_success(self):
        """Test get() returns the correct value from _execute_with_retry."""
        manager = RedisManager()
        with patch.object(manager, '_execute_with_retry', return_value="the-stored-value") as mock_execute:
            result = manager.get("my-key")
            self.assertEqual(result, "the-stored-value")
            mock_execute.assert_called_once_with(RedisOperation.GET, "my-key")

    def test_get_returns_none_on_failure(self):
        """Test get() returns None and logs an error on failure."""
        manager = RedisManager()
        with patch.object(manager, '_execute_with_retry', side_effect=RedisError("Get failed")):
            result = manager.get("my-key")
            self.assertIsNone(result)
            self.mock_logger.error.assert_called_once_with(
                "Failed to get key", key="my-key", error="Get failed"
            )

    def test_delete_returns_true_on_success(self):
        """Test delete() returns True when a key is successfully deleted."""
        manager = RedisManager()
        with patch.object(manager, '_execute_with_retry', return_value=1) as mock_execute:
            result = manager.delete("my-key")
            self.assertTrue(result)
            mock_execute.assert_called_once_with(RedisOperation.DELETE, "my-key")

    def test_delete_returns_false_on_failure(self):
        """Test delete() returns False and logs an error on failure."""
        manager = RedisManager()
        with patch.object(manager, '_execute_with_retry', side_effect=RedisError("Delete failed")):
            result = manager.delete("my-key")
            self.assertFalse(result)
            self.mock_logger.error.assert_called_once_with(
                "Failed to delete key", key="my-key", error="Delete failed"
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
