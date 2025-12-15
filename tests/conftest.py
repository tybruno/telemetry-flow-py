"""Root test fixtures.

Shared fixtures for all tests.
"""

import pytest


@pytest.fixture
def sample_redis_url() -> str:
    """Sample Redis URL for testing."""
    return "redis://localhost:6379"


@pytest.fixture
def redis_url() -> str:
    """Redis URL for integration tests.

    Returns:
        Redis connection URL string
    """
    url = "redis://localhost:6379/0"
    return url


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
