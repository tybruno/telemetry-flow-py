"""Tests for Redis Store implementation."""

import pytest
from unittest.mock import AsyncMock
from datetime import timedelta

from src.storage.exceptions import StorageError
from src.storage.redis_store import RedisStore


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


class TestRedisStoreRetrieve:
    """Tests for retrieve operations."""

    @pytest.mark.asyncio
    async def test_retrieve_existing_key(self) -> None:
        """Test retrieving existing key."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.get = AsyncMock(return_value=b'{"data": "value"}')

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


class TestRedisStoreDelete:
    """Tests for delete operations."""

    @pytest.mark.asyncio
    async def test_delete_success(self) -> None:
        """Test successful delete."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.delete = AsyncMock(return_value=1)

        await store.delete(key="test_key")

        store._client.delete.assert_called_once()


class TestRedisStoreClose:
    """Tests for close operations."""

    @pytest.mark.asyncio
    async def test_close_success(self) -> None:
        """Test successful close."""
        store = RedisStore(url="redis://localhost:6379/0")
        store._client = AsyncMock()
        store._client.close = AsyncMock()
        store._client.aclose = AsyncMock()

        await store.close()

        # Just verify close was attempted
        assert store._client.close.called or store._client.aclose.called
