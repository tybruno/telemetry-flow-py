"""Tests for BaseAggregator abstract methods."""

import pytest

from src.aggregation.base_aggregator import BaseAggregator


class TestBaseAggregatorAbstract:
    """Test BaseAggregator abstract method behavior."""

    def test_cannot_instantiate_abstract_base_aggregator(self) -> None:
        """Test cannot instantiate BaseAggregator directly."""
        with pytest.raises(TypeError, match="abstract"):
            BaseAggregator(window_size_seconds=60)


__all__: list[str] = []
