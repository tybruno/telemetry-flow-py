"""Aggregation library test fixtures.

Provides test fixtures specific to aggregation library testing including
sample metrics, window configurations, and mock storage.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.core.protocols import StorageProtocol


@pytest.fixture
def mock_storage() -> Mock:
    """Mock StorageProtocol implementation for testing.

    Returns:
        Mock storage with async methods configured

    Example:
        async def test_aggregator(mock_storage):
            aggregator = TumblingWindowAggregator(storage=mock_storage, ...)
            mock_storage.store.assert_called_once()
    """
    storage = Mock(spec=StorageProtocol)
    storage.store = AsyncMock()
    storage.retrieve = AsyncMock(return_value=None)
    storage.delete = AsyncMock()
    return storage


@pytest.fixture
def sample_numeric_values() -> list[float]:
    """Sample numeric values for aggregation testing.

    Returns:
        List of sample metric values

    Example:
        def test_calculate_average(sample_numeric_values):
            avg = calculate_average(sample_numeric_values)
            assert avg == 85.0
    """
    raise NotImplementedError


@pytest.fixture
def window_config() -> dict:
    """Standard window configuration for testing.

    Returns:
        Dictionary with window size and related settings

    Example:
        def test_aggregator_init(window_config):
            aggregator = TumblingWindowAggregator(**window_config)
            assert aggregator.window_size_seconds == 60
    """
    raise NotImplementedError
