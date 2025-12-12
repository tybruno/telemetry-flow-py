"""Aggregation-specific data models.

This module defines generic models for windowed aggregation results. These
models are domain-agnostic and can represent aggregated metrics from any
numeric data stream.

Classes:
    WindowMetrics: Statistical aggregation results for a time window
    WindowBounds: Timestamp boundaries defining a window
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, kw_only=True, slots=True)
class WindowBounds:
    """Timestamp boundaries defining a time window.

    Represents the start and end times of an aggregation window. Used for
    tracking which events belong to which windows.

    Attributes:
        start: Window start timestamp (inclusive)
        end: Window end timestamp (exclusive)
        size_seconds: Window duration in seconds

    Example:
        bounds = WindowBounds(
            start=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
            end=datetime(2024, 1, 1, 12, 1, 0, tzinfo=UTC),
            size_seconds=60
        )
    """
    start: datetime
    end: datetime
    size_seconds: float


@dataclass(frozen=True, kw_only=True, slots=True)
class WindowMetrics:
    """Statistical aggregation results for a time window.

    Generic container for aggregated metrics including statistical measures.
    Domain-agnostic design works with any numeric metric stream.

    Attributes:
        window_bounds: Timestamp boundaries of this window
        average: Mean value of all metrics in window
        minimum: Lowest value in window
        maximum: Highest value in window
        stddev: Standard deviation of values
        count: Number of data points in window
        sum: Total sum of all values

    Example:
        metrics = WindowMetrics(
            window_bounds=bounds,
            average=85.5,
            minimum=75.0,
            maximum=95.0,
            stddev=5.2,
            count=120,
            sum=10260.0
        )
    """
    window_bounds: WindowBounds
    average: float
    minimum: float
    maximum: float
    stddev: float
    count: int
    sum: float


__all__ = ["WindowBounds", "WindowMetrics"]
