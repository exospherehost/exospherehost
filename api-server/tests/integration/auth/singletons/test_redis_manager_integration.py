"""
Integration tests for the RedisManager singleton class.

These tests are designed to be run against a live Redis instance to verify
real-world behavior. They are structured in a modular and extensible way
using a test class and pytest fixtures.

Prerequisites:
- A running Redis instance (e.g., via Docker: `docker run -d -p 6379:6379 redis`)
- `pytest` and `redis` packages installed.
"""
import pytest
import os
import uuid
import time
import sys
from collections.abc import Generator

# Get the absolute path to the api-server directory
api_server_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, api_server_dir)

from app.singletons.redis_manager import RedisManager
from app.singletons.RedisOperation import RedisOperation
from app.singletons.SingletonDecorator import singleton

# Mark all tests in this file as integration tests, allowing them to be run
# separately from unit tests (e.g., `pytest -m integration`).
pytestmark = pytest.mark.integration


@pytest.fixture #(scope="session")
def redis_manager_fixture() -> Generator[RedisManager, None, None]:
    """
    A session-scoped fixture that provides a single, clean RedisManager instance
    for the entire test session. It handles environment setup, singleton resetting,
    and database cleanup.
    """
    # --- Environment Setup ---
    # Store original environment variables to restore them after the test session.
    original_env = {
        'REDIS_HOST': os.environ.get('REDIS_HOST'),
        'REDIS_PORT': os.environ.get('REDIS_PORT'),
        'REDIS_PASSWORD': os.environ.get('REDIS_PASSWORD'),
        'REDIS_DB': os.environ.get('REDIS_DB')
    }

    # Configure the environment for a local test Redis instance.
    os.environ['REDIS_HOST'] = 'localhost'
    os.environ['REDIS_PORT'] = '6379'
    os.environ['REDIS_PASSWORD'] = ''  # Assumes no password for local test instance
    os.environ['REDIS_DB'] = '1'  # Use a dedicated DB to isolate tests.

    # --- Singleton and DB Reset ---
    # Access the internal dictionary of the singleton decorator and clear it.
    # This ensures we get a fresh instance.
    if hasattr(singleton, '__closure__') and singleton.__closure__:
        for cell in singleton.__closure__:
            if isinstance(cell.cell_contents, dict):
                cell.cell_contents.clear()
                break

    # --- Fixture Provision ---
    # Initialize the manager and ensure the connection is live.
    try:
        manager = RedisManager()
        client = manager.get_client()
        client.ping()
    except Exception as e:
        pytest.fail(
            "Could not initialize RedisManager. Is Redis running and accessible? "
            f"Error: {e}"
        )

    # Yield the manager instance to the tests.
    yield manager

    # --- Teardown ---
    # Flush the test database after all tests in the session are complete.
    client.flushdb()

    # Restore the original environment variables.
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]


class TestRedisManagerIntegration:
    """
    A test class to group all integration tests for the RedisManager.
    This modular structure makes the tests more organized and readable.
    """

    @staticmethod
    def _generate_key(prefix: str) -> str:
        """Helper method to create unique keys for each test."""
        return f"test:{prefix}:{uuid.uuid4()}"

    def test_singleton_pattern_is_maintained(self, redis_manager_fixture: RedisManager):
        """
        Verify that multiple calls to RedisManager() return the exact same
        object instance, confirming the singleton pattern works as expected.
        """
        # The fixture already created the first instance.
        manager1 = redis_manager_fixture
        # Calling it again should return the cached instance.
        manager2 = RedisManager()

        assert manager1 is manager2, "RedisManager did not return the same instance."
        assert manager1.get_client() is manager2.get_client(), "Clients from different calls are not the same instance."

    def test_set_and_get_value(self, redis_manager_fixture: RedisManager):
        """
        Test the fundamental set and get operations to ensure data integrity.
        """
        test_key = self._generate_key("set_get")
        test_value = f"value-{uuid.uuid4()}"

        # Set a value with a standard TTL.
        set_success = redis_manager_fixture.set_with_ttl(test_key, test_value, 60)
        assert set_success, "set_with_ttl should return True on success."

        # Retrieve the value and verify it's correct.
        retrieved_value = redis_manager_fixture.get(test_key)
        assert retrieved_value == test_value, "get should retrieve the exact value that was set."

    def test_exists_operation(self, redis_manager_fixture: RedisManager):
        """
        Verify the exists() method correctly identifies existing and
        non-existing keys.
        """
        existing_key = self._generate_key("exists_positive")
        non_existing_key = self._generate_key("exists_negative")

        # Set a key to ensure it exists.
        redis_manager_fixture.set_with_ttl(existing_key, "some_value", 10)

        # Assert that exists() returns True for the key we just set.
        assert redis_manager_fixture.exists(existing_key), "exists() should return True for a key that has been set."

        # Assert that exists() returns False for a key that has not been set.
        assert not redis_manager_fixture.exists(
            non_existing_key), "exists() should return False for a non-existent key."

    def test_delete_operation(self, redis_manager_fixture: RedisManager):
        """
        Verify that the delete() operation successfully removes a key and
        handles non-existent keys gracefully.
        """
        test_key = self._generate_key("delete")

        # Set a key to be deleted.
        redis_manager_fixture.set_with_ttl(test_key, "to_be_deleted", 10)
        assert redis_manager_fixture.exists(test_key), "Key should exist before deletion."

        # Delete the key and verify the operation's success.
        assert redis_manager_fixture.delete(test_key), "delete() should return True for an existing key."
        assert not redis_manager_fixture.exists(test_key), "Key should not exist after being deleted."

        # Attempting to delete a non-existent key should return False.
        assert not redis_manager_fixture.delete(test_key), "delete() should return False for a non-existent key."

    def test_ttl_expiration(self, redis_manager_fixture: RedisManager):
        """
        Verify that a key with a TTL correctly expires and is removed from
        the database after the specified time.
        """
        test_key = self._generate_key("ttl")
        ttl_seconds = 1  # Use a short TTL for a quick test.

        # Set the key with a 1-second TTL.
        redis_manager_fixture.set_with_ttl(test_key, "expiring_value", ttl_seconds)
        assert redis_manager_fixture.exists(test_key), "Key should exist immediately after being set."

        # Wait for a duration longer than the TTL to allow for expiration.
        time.sleep(ttl_seconds + 0.5)

        # Verify the key has expired and no longer exists.
        assert not redis_manager_fixture.exists(test_key), "Key should no longer exist after its TTL has passed."
