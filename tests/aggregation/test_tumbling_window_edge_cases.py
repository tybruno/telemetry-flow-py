"""Edge case tests for TumblingWindowAggregator."""

import math
from datetime import datetime, timezone

import pytest

from src.aggregation.tumbling_window import TumblingWindowAggregator
from src.core.models import TelemetryEvent


class TestTumblingWindowAggregatorEdgeCases:
    """Test edge cases for TumblingWindowAggregator."""

    @pytest.fixture
    def aggregator(self) -> TumblingWindowAggregator:
        """Create aggregator instance.

        Returns:
            TumblingWindowAggregator instance.
        """
        return TumblingWindowAggregator(window_size=60)

    async def test_aggregate_with_infinite_value_raises(
        self,
        aggregator: TumblingWindowAggregator,
    ) -> None:
        """Test aggregator raises on infinite metric value.

        Args:
            aggregator: TumblingWindowAggregator fixture.
        """
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=math.inf,
            timestamp=datetime(2025, 12, 12, 10, 0, 30, tzinfo=timezone.utc),
        )

        with pytest.raises(ValueError, match="Metric value must be finite"):
            await aggregator.aggregate(event)

    async def test_aggregate_with_nan_value_raises(
        self,
        aggregator: TumblingWindowAggregator,
    ) -> None:
        """Test aggregator raises on NaN metric value.

        Args:
            aggregator: TumblingWindowAggregator fixture.
        """
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=math.nan,
            timestamp=datetime(2025, 12, 12, 10, 0, 30, tzinfo=timezone.utc),
        )

        with pytest.raises(ValueError, match="Metric value must be finite"):
            await aggregator.aggregate(event)


__all__: list[str] = []
