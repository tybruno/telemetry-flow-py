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

import logging as _log
import math
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
    _windows: dict[tuple[str, str, str], dict[str, object]]

    def __init__(self, *, window_size: int) -> None:
        """Initialize aggregator with window size.

        Args:
            window_size: Window duration in seconds.

        Raises:
            ValueError: If window_size not positive.
        """
        super().__init__(window_size)
        self._window_size = window_size
        self._window_delta = timedelta(seconds=window_size)
        self._windows = {}
        _log.info("Tumbling window aggregator initialized: window_size=%d", window_size)

    async def aggregate(self, event: TelemetryEvent) -> WindowMetrics | None:
        """Aggregate event into time window.

        Args:
            event: Telemetry event to aggregate.

        Returns:
            WindowMetrics if window completed, None if still accumulating.

        Raises:
            ValueError: If event has invalid timestamp or metric value.
        """
        self._validate_event(event)

        window_key = self._generate_window_key(
            event.device_id,
            event.interface,
            event.metric_name
        )

        window_start = self._align_to_window_start(event.timestamp)
        window_end = self._calculate_window_end(window_start)

        completed_metrics = self._check_window_boundary(
            window_key,
            event,
            window_start,
            window_end
        )

        if completed_metrics:
            finalized_metrics = completed_metrics
            return finalized_metrics

        existing_window = self._windows.get(window_key)
        if not existing_window:
            self._init_window(window_key, event, window_start, window_end)
            return None

        self._accumulate_event(existing_window, event)
        return None

    def _validate_event(self, event: TelemetryEvent) -> None:
        """Validate event for aggregation.

        Args:
            event: Event to validate.

        Raises:
            ValueError: If event is invalid.
        """
        if not math.isfinite(event.metric_value):
            error_message = "Metric value must be finite: %s"
            _log.error(error_message, event.metric_value)
            raise ValueError(error_message % event.metric_value) from None

    def _check_window_boundary(
        self,
        window_key: tuple[str, str, str],
        event: TelemetryEvent,
        window_start: object,
        window_end: object,
    ) -> WindowMetrics | None:
        """Check if window boundary crossed and finalize if needed.

        Args:
            window_key: Window identifier tuple.
            event: Current event being processed.
            window_start: Calculated start of current window.
            window_end: Calculated end of current window.

        Returns:
            WindowMetrics if old window finalized, None otherwise.
        """
        existing_window = self._windows.get(window_key)

        if not existing_window:
            no_window_completed = None
            return no_window_completed

        existing_start = existing_window["start"]
        boundary_crossed = window_start != existing_start

        if boundary_crossed:
            completed_metrics = self._finalize_window(window_key, existing_window)
            self._init_window(window_key, event, window_start, window_end)
            return completed_metrics

        no_window_completed = None
        return no_window_completed

    def _init_window(
        self,
        window_key: tuple[str, str, str],
        event: TelemetryEvent,
        window_start: object,
        window_end: object,
    ) -> None:
        """Initialize new window with first event.

        Args:
            window_key: Window identifier tuple.
            event: First event in window.
            window_start: Window start timestamp.
            window_end: Window end timestamp.
        """
        self._windows[window_key] = {
            "start": window_start,
            "end": window_end,
            "values": [event.metric_value],
            "sum": event.metric_value,
            "count": 1,
            "min": event.metric_value,
            "max": event.metric_value,
        }
        _log.debug(
            "Initialized window: key=%s, start=%s, value=%f",
            window_key,
            window_start,
            event.metric_value
        )

    def _accumulate_event(
        self,
        window: dict[str, object],
        event: TelemetryEvent,
    ) -> None:
        """Accumulate event into existing window.

        Args:
            window: Window state dictionary.
            event: Event to accumulate.
        """
        values = window["values"]
        assert isinstance(values, list)
        values.append(event.metric_value)

        current_sum = window["sum"]
        assert isinstance(current_sum, (int, float))
        window["sum"] = current_sum + event.metric_value

        current_count = window["count"]
        assert isinstance(current_count, int)
        window["count"] = current_count + 1

        current_min = window["min"]
        assert isinstance(current_min, (int, float))
        window["min"] = min(current_min, event.metric_value)

        current_max = window["max"]
        assert isinstance(current_max, (int, float))
        window["max"] = max(current_max, event.metric_value)

    def _finalize_window(
        self,
        window_key: tuple[str, str, str],
        window: dict[str, object],
    ) -> WindowMetrics:
        """Finalize and compute window metrics.

        Args:
            window_key: Window identifier tuple.
            window: Window state dictionary.

        Returns:
            Computed window metrics.
        """
        values = self._extract_window_values(window)
        stats = self._calculate_statistics(values, window)
        bounds, device_id, interface, metric_name = self._create_window_bounds(window, window_key)

        metrics = WindowMetrics(
            device_id=device_id,
            interface=interface,
            metric_name=metric_name,
            window_bounds=bounds,
            average=stats["average"],
            minimum=stats["minimum"],
            maximum=stats["maximum"],
            stddev=stats["stddev"],
            count=int(stats["count"]),
            sum=stats["sum"]
        )

        self._log_window_completion(window_key, stats)

        del self._windows[window_key]

        return metrics

    def _extract_window_values(
        self,
        window: dict[str, object]
    ) -> list[float]:
        """Extract values from window state.

        Args:
            window: Window state dictionary.

        Returns:
            List of metric values.
        """
        values = window["values"]
        assert isinstance(values, list)
        return values

    def _calculate_statistics(
        self,
        values: list[float],
        window: dict[str, object]
    ) -> dict[str, float]:
        """Calculate statistical metrics for window.

        Args:
            values: List of metric values.
            window: Window state dictionary.

        Returns:
            Dictionary with calculated statistics.
        """
        count = window["count"]
        assert isinstance(count, int)

        total_sum = window["sum"]
        assert isinstance(total_sum, (int, float))

        minimum = window["min"]
        assert isinstance(minimum, (int, float))

        maximum = window["max"]
        assert isinstance(maximum, (int, float))

        average = total_sum / count
        stddev = self._calculate_stddev(values, average, count)

        statistics = {
            "average": average,
            "minimum": minimum,
            "maximum": maximum,
            "stddev": stddev,
            "count": count,
            "sum": total_sum
        }
        return statistics

    def _calculate_stddev(
        self,
        values: list[float],
        mean: float,
        count: int
    ) -> float:
        """Calculate standard deviation.

        Args:
            values: List of metric values.
            mean: Average value.
            count: Number of values.

        Returns:
            Standard deviation.
        """
        if count <= 1:
            standard_deviation = 0.0
            return standard_deviation

        variance = sum((x - mean) ** 2 for x in values) / count
        standard_deviation = math.sqrt(variance)
        return standard_deviation

    def _create_window_bounds(
        self,
        window: dict[str, object],
        window_key: tuple[str, str, str]
    ) -> tuple[WindowBounds, str, str, str]:
        """Create window bounds and extract context from window state.

        Args:
            window: Window state dictionary.
            window_key: Window identifier (device_id, interface, metric_name).

        Returns:
            Tuple of (WindowBounds, device_id, interface, metric_name).
        """
        from datetime import datetime

        start = window["start"]
        end = window["end"]

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)

        bounds = WindowBounds(
            start=start,
            end=end,
            size_seconds=float(self._window_size)
        )

        device_id, interface, metric_name = window_key

        return bounds, device_id, interface, metric_name

    def _log_window_completion(
        self,
        window_key: tuple[str, str, str],
        stats: dict[str, float]
    ) -> None:
        """Log window completion details.

        Args:
            window_key: Window identifier.
            stats: Calculated statistics.
        """
        _log.info(
            "Window finalized: key=%s, count=%d, avg=%f, min=%f, max=%f",
            window_key,
            int(stats["count"]),
            stats["average"],
            stats["minimum"],
            stats["maximum"]
        )


__all__ = ["TumblingWindowAggregator"]
