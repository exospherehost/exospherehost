import redis
import os
import time
from typing import Any, Optional
from redis.exceptions import RedisError, ConnectionError, TimeoutError

from .RedisOperation import RedisOperation
from .SingletonDecorator import singleton
from .logs_manager import LogsManager


@singleton
class RedisManager:
    """
    Redis client manager singleton that provides a centralized interface for Redis operations.
    Handles connection management, retries, and proper error logging.
    """

    def __init__(self) -> None:
        """
        Initialize Redis connection with environment-based configuration.
        Validates connection on startup.
        """
        self.logger = LogsManager().get_logger()
        self.max_retries = int(os.getenv("REDIS_MAX_RETRIES", 3))
        self.retry_delay = float(os.getenv("REDIS_RETRY_DELAY", 0.5))

        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis-master"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD", ""),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )

        self._validate_connection()

    def _validate_connection(self) -> bool:
        """
        Test the Redis connection with retries.

        Returns:
            bool: True if connection successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                self.client.ping()
                return True
            except ConnectionError as e:
                self.logger.error("Redis connection failed",
                                  attempt=attempt + 1,
                                  max_attempts=self.max_retries,
                                  error=str(e))
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        self.logger.error("All Redis connection attempts failed")
        return False

    def get_client(self) -> redis.Redis:
        """
        Get the underlying Redis client.

        Returns:
            redis.Redis: The Redis client instance
        """
        return self.client

    def _execute_with_retry(self, operation: RedisOperation, *args, **kwargs) -> Any:
        """
        Execute Redis operation with retry logic.

        Args:
            operation: Name of the Redis operation to perform
            *args: Arguments to pass to the Redis operation
            **kwargs: Keyword arguments to pass to the Redis operation

        Returns:
            Any: Result of the Redis operation
        """
        for attempt in range(self.max_retries):
            try:
                method = getattr(self.client, operation.value)
                return method(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                self.logger.warning(
                    "Redis operation failed, retrying",
                    operation=operation,
                    attempt=attempt + 1,
                    max_attempts=self.max_retries,
                    error=str(e)
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        self.logger.error("Redis operation failed after retries", operation=operation)
        raise RedisError(f"Operation {operation} failed after {self.max_retries} attempts")

    def set_with_ttl(self, key: str, value: str, ttl_seconds: int) -> bool:
        """
        Set a key with TTL in seconds.

        Args:
            key: Redis key name
            value: Value to store
            ttl_seconds: Time-to-live in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self._execute_with_retry(RedisOperation.SET, key, value, ex=ttl_seconds)
        except RedisError as e:
            self.logger.error("Failed to set key with TTL",
                              key=key,
                              ttl_seconds=ttl_seconds,
                              error=str(e))
            return False

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.

        Args:
            key: Redis key name

        Returns:
            bool: True if key exists, False otherwise
        """
        try:
            return self._execute_with_retry(RedisOperation.EXISTS, key) > 0
        except RedisError as e:
            self.logger.error("Failed to check key existence", key=key, error=str(e))
            return False

    def get(self, key: str) -> Optional[str]:
        """
        Get a value by key.

        Args:
            key: Redis key name

        Returns:
            Optional[str]: Value if found, None otherwise
        """
        try:
            return self._execute_with_retry(RedisOperation.GET, key)
        except RedisError as e:
            self.logger.error("Failed to get key", key=key, error=str(e))
            return None

    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.

        Args:
            key: Redis key name

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            return bool(self._execute_with_retry(RedisOperation.DELETE, key))
        except RedisError as e:
            self.logger.error("Failed to delete key", key=key, error=str(e))
            return False