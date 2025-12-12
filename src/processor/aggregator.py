"""Time-window aggregation for telemetry metrics.

Class:
    TumblingWindowAggregator: Tumbling window aggregation.
"""

import logging
from datetime import timedelta

from src.core.models import TelemetryEvent
from src.processor.models import AggregatedMetric, WindowState

_log = logging.getLogger(__name__)


class TumblingWindowAggregator:
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

    __slots__ = ("_window_size", "_window_delta", "_windows")

    _window_size: int
    _window_delta: timedelta
    _windows: dict[tuple[str, str, str], WindowState]

    def __init__(self, *, window_size: int) -> None:
        """Initialize aggregator with window size.

        Args:
            window_size: Window duration in seconds.

        Raises:
            ValueError: If window_size not positive.
        """
        raise NotImplementedError

    async def aggregate(self, event: TelemetryEvent) -> AggregatedMetric | None:
        """Aggregate event into time window.

        Args:
            event: Telemetry event to aggregate.

        Returns:
            AggregatedMetric if window completed, None if still accumulating.
        """
        raise NotImplementedError


__all__ = ["TumblingWindowAggregator"]
