"""Integration tests for Redis storage operations.

Tests generic storage operations with real Redis instance.
"""

import pytest
from redis.asyncio import Redis

from src.storage.redis_store import RedisStore


@pytest.mark.integration
@pytest.mark.asyncio
class TestStorageIntegration:
    """Integration tests for Redis storage."""

    async def test_store_and_retrieve_value(self, redis_url: str) -> None:
        """Test storing and retrieving dictionary values."""
        redis_client = Redis.from_url(redis_url, decode_responses=False)
        storage = RedisStore(url=redis_url)

        test_key = "test:storage:key1"
        test_value = {"count": 5, "sum": 375.0, "average": 75.0}

        # Store value
        await storage.set(test_key, test_value)

        # Retrieve value
        retrieved = await storage.retrieve(test_key)
        assert retrieved is not None
        assert retrieved["count"] == 5
        assert retrieved["sum"] == 375.0
        assert retrieved["average"] == 75.0

        # Cleanup
        await redis_client.delete(test_key)
        await redis_client.aclose()

    async def test_ttl_expiration(self, redis_url: str) -> None:
        """Test values expire after TTL."""
        redis_client = Redis.from_url(redis_url, decode_responses=False)
        storage = RedisStore(url=redis_url)

        test_key = "test:storage:ttl"
        test_value = {"data": "temporary"}

        # Store with 2-second TTL
        await storage.set(test_key, test_value, ttl=2)

        # Verify exists
        retrieved = await storage.retrieve(test_key)
        assert retrieved is not None

        # Wait for expiration
        import asyncio
        await asyncio.sleep(3)

        # Should be expired
        expired = await storage.retrieve(test_key)
        assert expired is None
        await redis_client.aclose()

    async def test_nonexistent_key(self, redis_url: str) -> None:
        """Test retrieving non-existent key returns None."""
        redis_client = Redis.from_url(redis_url, decode_responses=False)
        storage = RedisStore(url=redis_url)

        test_key = "test:storage:nonexistent"
        retrieved = await storage.retrieve(test_key)
        assert retrieved is None
        await redis_client.aclose()

    async def test_update_existing_value(self, redis_url: str) -> None:
        """Test updating an existing key."""
        redis_client = Redis.from_url(redis_url, decode_responses=False)
        storage = RedisStore(url=redis_url)

        test_key = "test:storage:update"
        initial_value = {"count": 1, "sum": 50.0}
        updated_value = {"count": 2, "sum": 130.0}

        # Store initial
        await storage.set(test_key, initial_value)

        # Update
        await storage.set(test_key, updated_value)

        # Verify update
        retrieved = await storage.retrieve(test_key)
        assert retrieved is not None
        assert retrieved["count"] == 2
        assert retrieved["sum"] == 130.0

        # Cleanup
        await redis_client.aclose()

    async def test_concurrent_operations(self, redis_url: str) -> None:
        """Test concurrent storage operations."""
        import asyncio

        redis_client = Redis.from_url(redis_url, decode_responses=False)
        storage = RedisStore(url=redis_url)

        async def store_value(key_num: int):
            test_key = f"test:storage:concurrent:{key_num}"
            test_value = {"id": key_num, "value": float(key_num * 10)}
            await storage.set(test_key, test_value)
            retrieved = await storage.retrieve(test_key)
            return retrieved is not None and retrieved["id"] == key_num

        # Perform 10 concurrent operations
        tasks = [store_value(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(results)
        await redis_client.aclose()
