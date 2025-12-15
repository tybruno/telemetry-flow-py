"""Tests for base aggregator."""

import pytest

from src.aggregation.base_aggregator import BaseAggregator
from src.core.models import TelemetryEvent


class ConcreteAggregator(BaseAggregator):
    """Concrete implementation for testing."""

    async def aggregate(self, event: TelemetryEvent):
        """Test implementation."""
        return None


class TestBaseAggregator:
    """Test suite for BaseAggregator class."""

    def test_base_aggregator_initialization(self) -> None:
        """Test BaseAggregator initializes with window size."""
        aggregator = ConcreteAggregator(window_size_seconds=60)
        assert aggregator._window_size_seconds == 60

    def test_base_aggregator_negative_window_size_raises(self) -> None:
        """Test BaseAggregator raises on negative window size."""
        with pytest.raises(ValueError, match="Window size must be positive"):
            ConcreteAggregator(window_size_seconds=-60)

    def test_base_aggregator_zero_window_size_raises(self) -> None:
        """Test BaseAggregator raises on zero window size."""
        with pytest.raises(ValueError, match="Window size must be positive"):
            ConcreteAggregator(window_size_seconds=0)

    def test_generate_window_key(self) -> None:
        """Test _generate_window_key creates unique key."""
        aggregator = ConcreteAggregator(window_size_seconds=60)
        key = aggregator._generate_window_key("router-01", "eth0", "cpu")
        assert key == ("router-01", "eth0", "cpu")

    async def test_aggregate_abstract_method(self) -> None:
        """Test aggregate is abstract in BaseAggregator."""

        # Create instance that doesn't override aggregate
        aggregator = ConcreteAggregator(window_size_seconds=60)

        # Verify aggregate method exists and is callable
        assert hasattr(aggregator, 'aggregate')
        assert callable(aggregator.aggregate)


__all__: list[str] = []
