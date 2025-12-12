"""Root test fixtures.

Shared fixtures for all tests.
"""

import pytest


@pytest.fixture
def sample_redis_url() -> str:
    """Sample Redis URL for testing."""
    return "redis://localhost:6379"


__all__: list[str] = []
