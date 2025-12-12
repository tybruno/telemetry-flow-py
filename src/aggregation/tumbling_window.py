"""Time-window aggregation for telemetry metrics.

This module provides tumbling window aggregation for telemetry events,
calculating statistical metrics over fixed-size, non-overlapping time
windows.

Classes:
    TumblingWindowAggregator: Tumbling window aggregation implementation.

Example:
    Basic usage of tumbling window aggregation::

        from aggregation import TumblingWindowAggregator
        from core.models import TelemetryEvent
        from datetime import datetime, timezone

        aggregator = TumblingWindowAggregator(window_size=60)

        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc)
        )

        result = await aggregator.aggregate(event)
        if result:  # Window completed
            print(f"Average: {result.avg_value}")
"""

from datetime import timedelta

from src.aggregation.base_aggregator import BaseAggregator
from src.aggregation.models import WindowBounds, WindowMetrics
from src.core.models import TelemetryEvent


class TumblingWindowAggregator(BaseAggregator):
    """Tumbling window aggregator for telemetry metrics.

    Aggregates metrics over fixed-size time windows without overlap.
    Maintains separate state per (device_id, interface, metric_name).

    Attributes:
        _window_size: Window duration in seconds.
        _window_delta: Timedelta representation of window size.
        _windows: Per-device/interface/metric window tracking.
            Key: (device_id, interface, metric_name)
            Value: WindowState for active window.

    Example:
        aggregator = TumblingWindowAggregator(window_size=60)

        result = await aggregator.aggregate(event)
        if result:
            # Window completed
            print(f"Avg: {result.avg_value}")
    """

    __slots__ = ("_window_delta", "_window_size", "_windows")

    _window_size: int
    _window_delta: timedelta
    _windows: dict[tuple[str, str, str], WindowBounds]

    def __init__(self, *, window_size: int) -> None:
        """Initialize aggregator with window size.

        Args:
            window_size: Window duration in seconds.

        Raises:
            ValueError: If window_size not positive.
        """
        raise NotImplementedError

    async def aggregate(self, event: TelemetryEvent) -> WindowMetrics | None:
        """Aggregate event into time window.

        Args:
            event: Telemetry event to aggregate.

        Returns:
            WindowMetrics if window completed, None if still accumulating.

        Raises:
            ValueError: If event has invalid timestamp or metric value.
        """
        raise NotImplementedError


__all__ = ["TumblingWindowAggregator"]
