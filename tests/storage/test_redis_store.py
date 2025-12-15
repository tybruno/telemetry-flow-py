"""Tests for Redis Store implementation."""

from unittest.mock import AsyncMock

import pytest

from src.storage.exceptions import StorageError
from src.storage.redis_store import RedisStore


class TestRedisStoreInitialization:
    """Tests for RedisStore initialization."""

    def test_init_success(self) -> None:
        """Test successful initialization."""
        store = RedisStore(url="redis://localhost:6379/0")

        assert store._url == "redis://localhost:6379/0"
        assert store._client is not None

    def test_init_empty_url(self) -> None:
        """Test initialization with empty URL."""
        with pytest.raises(ValueError, match="Redis URL cannot be empty"):
            RedisStore(url="")

    def test_init_whitespace_url(self) -> None:
        """Test initialization with whitespace-only URL."""
        with pytest.raises(ValueError, match="Redis URL cannot be empty"):
            RedisStore(url="   ")


class TestRedisStoreSet:
    """Tests for set operations."""

    @pytest.mark.asyncio
    async def test_set_success(self) -> None:
        """Test successful set operation."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(return_value=True)

        await store.set(key="test_key", value={"data": "value"})

        store._client.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_with_ttl(self) -> None:
        """Test set operation with TTL."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.setex = AsyncMock(return_value=True)

        await store.set(key="test_key", value={"data": "value"}, ttl=3600)

        store._client.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_serialization_error(self) -> None:
        """Test set with non-serializable value."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()

        non_serializable = {"data": set()}

        with pytest.raises(ValueError, match="Failed to serialize value"):
            await store.set(key="test_key", value=non_serializable)

    @pytest.mark.asyncio
    async def test_set_redis_error(self) -> None:
        """Test set operation with Redis error."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(StorageError, match="Redis SET failed"):
            await store.set(key="test_key", value={"data": "value"})

    @pytest.mark.asyncio
    async def test_set_redis_error_with_ttl(self) -> None:
        """Test set with TTL operation with Redis error."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.setex = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(StorageError, match="Redis SET failed"):
            await store.set(key="test_key", value={"data": "value"}, ttl=3600)


class TestRedisStoreRetrieve:
    """Tests for retrieve operations."""

    @pytest.mark.asyncio
    async def test_retrieve_existing_key(self) -> None:
        """Test retrieving existing key."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value='{"data": "value"}')

        value = await store.retrieve(key="test_key")

        assert value == {"data": "value"}

    @pytest.mark.asyncio
    async def test_retrieve_non_existent_key(self) -> None:
        """Test retrieving non-existent key."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value=None)

        value = await store.retrieve(key="missing_key")

        assert value is None

    @pytest.mark.asyncio
    async def test_retrieve_invalid_json(self) -> None:
        """Test retrieve with invalid JSON."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value="not valid json")

        with pytest.raises(StorageError, match="Failed to deserialize value"):
            await store.retrieve(key="test_key")

    @pytest.mark.asyncio
    async def test_retrieve_redis_error(self) -> None:
        """Test retrieve operation with Redis error."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(StorageError, match="Redis GET failed"):
            await store.retrieve(key="test_key")


class TestRedisStoreDelete:
    """Tests for delete operations."""

    @pytest.mark.asyncio
    async def test_delete_success(self) -> None:
        """Test successful delete."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.delete = AsyncMock(return_value=1)

        result = await store.delete(key="test_key")

        assert result is True
        store._client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_non_existent_key(self) -> None:
        """Test delete of non-existent key."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.delete = AsyncMock(return_value=0)

        result = await store.delete(key="missing_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_redis_error(self) -> None:
        """Test delete operation with Redis error."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.delete = AsyncMock(side_effect=Exception("Connection failed"))

        with pytest.raises(StorageError, match="Redis DELETE failed"):
            await store.delete(key="test_key")


class TestRedisStoreClose:
    """Tests for close operations."""

    @pytest.mark.asyncio
    async def test_close_success(self) -> None:
        """Test successful close."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.close = AsyncMock()

        await store.close()

        store._client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_error(self) -> None:
        """Test close operation with error."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.close = AsyncMock(side_effect=Exception("Close failed"))

        with pytest.raises(StorageError, match="Failed to close Redis connection"):
            await store.close()


class TestRedisStoreProtocolMethods:
    """Tests for StorageProtocol compatibility methods."""

    @pytest.mark.asyncio
    async def test_store_method(self) -> None:
        """Test store method compatibility."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.set = AsyncMock(return_value=True)

        await store.store(key="test_key", value={"data": "value"})

        store._client.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_method(self) -> None:
        """Test get method compatibility."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value='{"data": "value"}')

        value = await store.get(key="test_key")

        assert value == {"data": "value"}

    @pytest.mark.asyncio
    async def test_get_method_none(self) -> None:
        """Test get method returns None for missing key."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value=None)

        value = await store.get(key="missing_key")

        assert value is None
