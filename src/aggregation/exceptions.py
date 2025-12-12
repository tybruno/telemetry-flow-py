"""Aggregation-specific exceptions.

This module defines all exception types raised by the aggregation library,
allowing for both specific and broad error handling.

Classes:
    AggregationError: Base exception for all aggregation errors
    WindowError: Raised when window operations fail
    InvalidMetricError: Raised when metric data is invalid
    StateError: Raised when window state operations fail

Example:
    Handling aggregation exceptions::

        try:
            result = await aggregator.aggregate(event)
        except InvalidMetricError as e:
            _log.error("Invalid metric data: %s", e)
        except AggregationError as e:
            _log.error("Aggregation error: %s", e)
"""
from src.core.exceptions import TelemetryError


class AggregationError(TelemetryError):
    """Base exception for all aggregation-related errors.

    All aggregation exceptions inherit from this base, allowing catch-all
    exception handling when needed.

    Example:
        try:
            await aggregator.process()
        except AggregationError as e:
            _log.error("Aggregation error occurred: %s", e)
    """


class WindowError(AggregationError):
    """Raised when window operations fail.

    Indicates problems with window boundary calculations, window state
    management, or window transitions.

    Example:
        if window_end <= window_start:
            raise WindowError(
                f"Invalid window: end {window_end} <= start {window_start}"
            )
    """


class InvalidMetricError(AggregationError):
    """Raised when metric data is invalid for aggregation.

    Metric values don't meet requirements (e.g., non-numeric, negative
    when positive required, out of valid range).

    Example:
        if not isinstance(value, (int, float)):
            raise InvalidMetricError(
                f"Expected numeric value, got {type(value).__name__}"
            )
    """


class StateError(AggregationError):
    """Raised when window state operations fail.

    Problems persisting or retrieving window state from storage,
    or state corruption detected.

    Example:
        if state is None:
            raise StateError(f"Failed to retrieve state for window {key}")
    """


__all__ = [
    "AggregationError",
    "WindowError",
    "InvalidMetricError",
    "StateError",
]
