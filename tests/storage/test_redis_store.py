"""Tests for Redis Store implementation.

Tests the RedisStore class for state persistence including set, get,
delete operations and error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import timedelta

from src.storage.exceptions import StorageError
from src.storage.redis_store import RedisStore


class TestRedisStoreInitialization:
    """Tests for RedisStore initialization."""

    def test_init_with_valid_url(self) -> None:
        """Test initialization with valid Redis URL."""
        store = RedisStore(url="redis://localhost:6379/0")
        
        assert store._url == "redis://localhost:6379/0"
        assert store._client is not None

    def test_init_with_empty_url_raises(self) -> None:
        """Test initialization with empty URL raises ValueError."""
        with pytest.raises(ValueError, match="Redis URL cannot be empty"):
            RedisStore(url="")

    def test_init_with_whitespace_url_raises(self) -> None:
        """Test initialization with whitespace URL raises ValueError."""
        with pytest.raises(ValueError, match="Redis URL cannot be empty"):
            RedisStore(url="   ")


class TestRedisStoreSet:
    """Tests for RedisStore set method."""

    @pytest.mark.asyncio
    async def test_set_without_ttl(self) -> None:
        """Test set operation without TTL."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(return_value=True)

        await store.set(key="counter:device-01", value="42")

        store._client.set.assert_called_once_with("counter:device-01", "42")

    @pytest.mark.asyncio
    async def test_set_with_ttl(self) -> None:
        """Test set operation with TTL."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(return_value=True)

        ttl = timedelta(seconds=300)
        await store.set(key="session:abc123", value="active", ttl=ttl)

        store._client.set.assert_called_once_with(
            "session:abc123",
            "active",
            ex=ttl
        )

    @pytest.mark.asyncio
    async def test_set_with_empty_key_raises(self) -> None:
        """Test set with empty key raises ValueError."""
        store = RedisStore(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Key cannot be empty"):
            await store.set(key="", value="data")

    @pytest.mark.asyncio
    async def test_set_redis_error_raises_storage_error(self) -> None:
        """Test Redis error during set raises StorageError."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(StorageError, match="Failed to set"):
            await store.set(key="key1", value="value1")


class TestRedisStoreRetrieve:
    """Tests for RedisStore retrieve method."""

    @pytest.mark.asyncio
    async def test_retrieve_existing_key(self) -> None:
        """Test retrieve returns value for existing key."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value=b"stored_value")

        value = await store.retrieve(key="counter:device-01")

        assert value == "stored_value"
        store._client.get.assert_called_once_with("counter:device-01")

    @pytest.mark.asyncio
    async def test_retrieve_non_existent_key_returns_none(self) -> None:
        """Test retrieve returns None for non-existent key."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value=None)

        value = await store.retrieve(key="missing:key")

        assert value is None
        store._client.get.assert_called_once_with("missing:key")

    @pytest.mark.asyncio
    async def test_retrieve_with_empty_key_raises(self) -> None:
        """Test retrieve with empty key raises ValueError."""
        store = RedisStore(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Key cannot be empty"):
            await store.retrieve(key="")

    @pytest.mark.asyncio
    async def test_retrieve_redis_error_raises_storage_error(self) -> None:
        """Test Redis error during retrieve raises StorageError."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(side_effect=Exception("Network error"))

        with pytest.raises(StorageError, match="Failed to retrieve"):
            await store.retrieve(key="key1")


class TestRedisStoreDelete:
    """Tests for RedisStore delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing_key(self) -> None:
        """Test delete removes existing key."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.delete = AsyncMock(return_value=1)

        await store.delete(key="old:session")

        store._client.delete.assert_called_once_with("old:session")

    @pytest.mark.asyncio
    async def test_delete_non_existent_key(self) -> None:
        """Test delete on non-existent key doesn't raise."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.delete = AsyncMock(return_value=0)

        # Should not raise even if key doesn't exist
        await store.delete(key="missing:key")

        store._client.delete.assert_called_once_with("missing:key")

    @pytest.mark.asyncio
    async def test_delete_with_empty_key_raises(self) -> None:
        """Test delete with empty key raises ValueError."""
        store = RedisStore(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Key cannot be empty"):
            await store.delete(key="")

    @pytest.mark.asyncio
    async def test_delete_redis_error_raises_storage_error(self) -> None:
        """Test Redis error during delete raises StorageError."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.delete = AsyncMock(side_effect=Exception("Timeout"))

        with pytest.raises(StorageError, match="Failed to delete"):
            await store.delete(key="key1")


class TestRedisStoreStore:
    """Tests for RedisStore store method (legacy alias)."""

    @pytest.mark.asyncio
    async def test_store_calls_set(self) -> None:
        """Test store method calls set (legacy alias)."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(return_value=True)

        await store.store(key="legacy:key", value="data")

        store._client.set.assert_called_once_with("legacy:key", "data")


class TestRedisStoreGet:
    """Tests for RedisStore get method (legacy alias)."""

    @pytest.mark.asyncio
    async def test_get_calls_retrieve(self) -> None:
        """Test get method calls retrieve (legacy alias)."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value=b"value")

        value = await store.get(key="legacy:key")

        assert value == "value"
        store._client.get.assert_called_once_with("legacy:key")


class TestRedisStoreClose:
    """Tests for RedisStore close method."""

    @pytest.mark.asyncio
    async def test_close_success(self) -> None:
        """Test successful store connection close."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.close = AsyncMock()
        store._client.connection_pool = MagicMock()
        store._client.connection_pool.disconnect = AsyncMock()

        await store.close()

        store._client.close.assert_called_once()
        store._client.connection_pool.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_with_error_logs_and_continues(self) -> None:
        """Test close with error logs but doesn't raise."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.close = AsyncMock(side_effect=Exception("Already closed"))

        # Should not raise - errors are logged
        await store.close()


class TestRedisStoreEdgeCases:
    """Tests for RedisStore edge cases and special values."""

    @pytest.mark.asyncio
    async def test_set_with_none_value(self) -> None:
        """Test set with None value stores as string 'None'."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(return_value=True)

        await store.set(key="nullable", value=None)

        # None is converted to string by Redis client
        store._client.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_numeric_value(self) -> None:
        """Test set with numeric value."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(return_value=True)

        await store.set(key="counter", value=42)

        store._client.set.assert_called_once_with("counter", 42)

    @pytest.mark.asyncio
    async def test_retrieve_numeric_value(self) -> None:
        """Test retrieve returns numeric values as strings."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value=b"42")

        value = await store.retrieve(key="counter")

        assert value == "42"  # Retrieved as string

    @pytest.mark.asyncio
    async def test_set_with_special_characters_in_key(self) -> None:
        """Test set with special characters in key."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(return_value=True)

        special_key = "device:router-01:interface:eth0/1:metric:cpu_usage"
        await store.set(key=special_key, value="85.5")

        store._client.set.assert_called_once_with(special_key, "85.5")
