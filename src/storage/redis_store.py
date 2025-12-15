"""Redis storage implementation.

This module provides a Redis-based implementation of the StorageProtocol
for state persistence and retrieval.

Classes:
    RedisStore: Redis implementation of StorageProtocol.

Example:
    Basic Redis storage usage::

        from storage import RedisStore

        store = RedisStore(url="redis://localhost:6379")

        # Store data
        await store.store("window:device-01", {"sum": 450.5})

        # Retrieve data
        data = await store.retrieve("window:device-01")
        print(f"Sum: {data['sum']}")

        # Delete data
        await store.delete("window:device-01")
"""

import json
import logging as _log
from typing import Any

import redis.asyncio as redis

from src.storage.base import BaseStorage
from src.storage.exceptions import StorageError


class RedisStore(BaseStorage):
    """Redis implementation of StorageProtocol.

    Implements state storage using Redis key-value operations with
    JSON serialization for dictionary values.

    Attributes:
        _url: Redis connection URL.
        _client: Redis async client instance.

    Example:
        Using Redis store for state persistence::

            store = RedisStore(url="redis://localhost:6379/0")

            # Store window state
            await store.set(
                key="window:router-01:eth0:bandwidth",
                value={"sum": 1250.5, "count": 15},
                ttl=3600
            )

            # Retrieve window state
            state = await store.retrieve("window:router-01:eth0:bandwidth")
            if state:
                avg = state["sum"] / state["count"]
    """

    __slots__ = ("_client", "_url")

    _url: str
    _client: redis.Redis  # type: ignore[type-arg]

    def __init__(self, *, url: str) -> None:
        """Initialize Redis store.

        Args:
            url: Redis connection URL (e.g., "redis://localhost:6379/0").

        Raises:
            ValueError: If URL is invalid or empty.
            ConnectionError: If Redis connection cannot be established.
        """
        if not url or not url.strip():
            error_message = "Redis URL cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        super().__init__(connection=None)
        self._url = url
        self._client = redis.from_url(url, decode_responses=True)
        _log.info("Redis store initialized: url=%s", url)

    async def set(
        self,
        key: str,
        value: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Store value in Redis with optional TTL.

        Args:
            key: Storage key.
            value: Dictionary value to store (will be JSON serialized).
            ttl: Optional time-to-live in seconds.

        Raises:
            ValueError: If key is empty or value cannot be serialized.
            StorageError: If Redis operation fails.
        """
        self._validate_key(key)
        self._log_operation("set", key)

        try:
            serialized_value = json.dumps(value)
        except (TypeError, ValueError) as e:
            error_message = "Failed to serialize value: %s"
            _log.error(error_message, str(e))
            raise ValueError(error_message % str(e)) from e

        try:
            if ttl is not None:
                await self._client.setex(key, ttl, serialized_value)
            else:
                await self._client.set(key, serialized_value)
            _log.debug("Stored key: %s", key)
        except Exception as e:
            error_message = "Redis SET failed: %s"
            _log.error(error_message, str(e))
            raise StorageError(error_message % str(e)) from e

    async def retrieve(self, key: str) -> dict[str, object] | None:
        """Retrieve value from Redis.

        Args:
            key: Storage key.

        Returns:
            Dictionary value if exists, None otherwise.

        Raises:
            ValueError: If key is empty.
            StorageError: If Redis operation fails or value cannot be
                deserialized.
        """
        self._validate_key(key)
        self._log_operation("retrieve", key)

        try:
            value = await self._client.get(key)
            if value is None:
                return None

            deserialized_value: dict[str, object] = json.loads(value)
            return deserialized_value
        except json.JSONDecodeError as e:
            error_message = "Failed to deserialize value: %s"
            _log.error(error_message, str(e))
            raise StorageError(error_message % str(e)) from e
        except Exception as e:
            error_message = "Redis GET failed: %s"
            _log.error(error_message, str(e))
            raise StorageError(error_message % str(e)) from e

    async def delete(self, key: str) -> bool:
        """Delete value from Redis.

        Args:
            key: Storage key to delete.

        Returns:
            True if key was deleted, False if key didn't exist.

        Raises:
            ValueError: If key is empty.
            StorageError: If Redis operation fails.
        """
        self._validate_key(key)
        self._log_operation("delete", key)

        try:
            result = await self._client.delete(key)
            was_deleted = result > 0
            return was_deleted
        except Exception as e:
            error_message = "Redis DELETE failed: %s"
            _log.error(error_message, str(e))
            raise StorageError(error_message % str(e)) from e

    async def store(self, key: str, value: Any) -> None:
        """Store a value with the given key (StorageProtocol compatibility).

        Args:
            key: Storage key identifier.
            value: Value to store (will be serialized).

        Raises:
            ValueError: If key is invalid.
            StorageError: If storage operation fails.
        """
        await self.set(key=key, value=value)

    async def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve a value by key (StorageProtocol compatibility).

        Args:
            key: Storage key to retrieve.

        Returns:
            Dictionary value if key exists, None otherwise.

        Raises:
            ValueError: If key is empty.
            StorageError: If retrieval operation fails.
        """
        result = await self.retrieve(key)
        return result

    async def close(self) -> None:
        """Close Redis connection.

        Cleanly closes the Redis client connection. Should be called
        during application shutdown.

        Raises:
            StorageError: If connection close fails.
        """
        try:
            await self._client.close()
            _log.info("Redis connection closed")
        except Exception as e:
            error_message = "Failed to close Redis connection: %s"
            _log.error(error_message, str(e))
            raise StorageError(error_message % str(e)) from e


__all__ = ["RedisStore"]
