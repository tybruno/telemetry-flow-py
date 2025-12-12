"""Base aggregator implementation with shared utilities.

This module provides an abstract base class for metric aggregator
implementations, offering shared window management and timestamp utilities
while allowing concrete classes to implement protocol-specific aggregation logic.

Classes:
    BaseAggregator: Abstract base class for aggregator implementations.
"""

import logging as _log
from abc import ABC, abstractmethod
from datetime import datetime

from src.core.models import TelemetryEvent
from src.processor.models import AggregatedMetric


class BaseAggregator(ABC):
    """Abstract base class for metric aggregator implementations.

    Provides shared window key generation and timestamp utilities for all
    aggregator implementations while enforcing core aggregation operations
    through abstract methods. Concrete classes inherit from this base and
    also satisfy the AggregatorProtocol contract.

    This hybrid approach combines:
    - Protocol: Defines contract for duck typing and flexible aggregation strategies
    - ABC: Provides shared implementation for window management utilities

    Attributes:
        _window_size_seconds: Size of aggregation window in seconds.

    Example:
        class TumblingWindowAggregator(BaseAggregator):
            def aggregate(self, event: TelemetryEvent) -> AggregatedMetric | None:
                window_key = self._generate_window_key(
                    event.device_id,
                    event.interface,
                    event.metric_name
                )
                # Tumbling window aggregation logic
                raise NotImplementedError
    """

    _window_size_seconds: int

    def __init__(self, window_size_seconds: int) -> None:
        """Initialize base aggregator with window size.

        Args:
            window_size_seconds: Size of aggregation window in seconds.

        Raises:
            ValueError: If window size is not positive.
        """
        raise NotImplementedError

    @abstractmethod
    def aggregate(self, event: TelemetryEvent) -> AggregatedMetric | None:
        """Aggregate telemetry event into time window.

        Must be implemented by concrete classes to provide specific
        aggregation strategies (tumbling, sliding, session windows, etc.).

        Args:
            event: Telemetry event to aggregate.

        Returns:
            Aggregated metric if window is complete, None otherwise.
        """
        raise NotImplementedError

    def _generate_window_key(
        self, device_id: str, interface: str, metric_name: str
    ) -> tuple[str, str, str]:
        """Generate unique key for window tracking.

        Shared utility for creating window keys based on device, interface,
        and metric dimensions. Ensures consistent window separation across
        aggregator types.

        Args:
            device_id: Device identifier.
            interface: Network interface name.
            metric_name: Metric name.

        Returns:
            Tuple key for window tracking.

        Example:
            key = self._generate_window_key("router-01", "eth0", "bandwidth")
            # ("router-01", "eth0", "bandwidth")
        """
        raise NotImplementedError

    def _align_to_window_start(self, timestamp: datetime) -> datetime:
        """Align timestamp to window boundary.

        Shared utility for calculating window start time by aligning
        timestamp to window boundaries. Used for consistent window
        tracking across events.

        Args:
            timestamp: Event timestamp to align.

        Returns:
            Window start timestamp aligned to boundary.

        Example:
            # With 60-second windows:
            event_time = datetime(2025, 12, 12, 10, 30, 45)
            window_start = self._align_to_window_start(event_time)
            # datetime(2025, 12, 12, 10, 30, 0)
        """
        raise NotImplementedError

    def _calculate_window_end(self, window_start: datetime) -> datetime:
        """Calculate window end time from window start.

        Shared utility for calculating when a window closes based on
        configured window size. Used for window completion detection.

        Args:
            window_start: Start timestamp of the window.

        Returns:
            Window end timestamp.

        Example:
            # With 60-second windows:
            start = datetime(2025, 12, 12, 10, 30, 0)
            end = self._calculate_window_end(start)
            # datetime(2025, 12, 12, 10, 31, 0)
        """
        raise NotImplementedError


__all__ = ["BaseAggregator"]
