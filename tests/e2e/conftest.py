"""End-to-end test fixtures."""

from collections.abc import AsyncIterator

import pytest
from redis.asyncio import Redis


@pytest.fixture
def redis_url() -> str:
    """Provide Redis URL for integration tests.
    
    Returns:
        Redis connection URL string
    """
    url = "redis://localhost:6379/0"
    return url


@pytest.fixture
async def redis_client() -> AsyncIterator[Redis]:
    """Provide Redis client for integration tests.
    
    Yields:
        Connected Redis client instance
    """
    client = Redis.from_url("redis://localhost:6379/0", decode_responses=False)
    yield client
    await client.aclose()


@pytest.fixture
def test_stream_name() -> str:
    """Provide unique stream name for each test.
    
    Returns:
        Stream name prefixed with test identifier
    """
    import uuid
    stream_name = f"test-stream-{uuid.uuid4().hex[:8]}"
    return stream_name


__all__: list[str] = []
