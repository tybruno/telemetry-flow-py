"""Processor service-specific data models.

Classes:
    WindowState: Aggregation window state.
    AggregatedMetric: Result of time-window aggregation.
    AnomalyResult: Detected anomaly information.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class WindowState:
    """Aggregation window state for tracking metrics over time.

    Attributes:
        device_id: Device identifier.
        metric_name: Metric being aggregated.
        window_start: Window start timestamp.
        window_end: Window end timestamp.
        metric_sum: Sum of metric values in window.
        metric_count: Number of events in window.
        min_value: Minimum value in window.
        max_value: Maximum value in window.
    """

    device_id: str
    metric_name: str
    window_start: datetime
    window_end: datetime
    metric_sum: float
    metric_count: int
    min_value: float
    max_value: float


@dataclass(frozen=True, slots=True, kw_only=True)
class AggregatedMetric:
    """Result of time-window aggregation.

    Attributes:
        device_id: Device identifier.
        metric_name: Metric name.
        avg_value: Average value over window.
        min_value: Minimum value in window.
        max_value: Maximum value in window.
        window_start: Window start timestamp.
        window_end: Window end timestamp.
        sample_count: Number of samples aggregated.
    """

    device_id: str
    metric_name: str
    avg_value: float
    min_value: float
    max_value: float
    window_start: datetime
    window_end: datetime
    sample_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class AnomalyResult:
    """Detected anomaly information.

    Attributes:
        device_id: Device where anomaly detected.
        metric_name: Metric that triggered anomaly.
        actual_value: Actual metric value.
        threshold: Threshold that was exceeded.
        severity: Anomaly severity level.
        detected_at: Timestamp of detection.
    """

    device_id: str
    metric_name: str
    actual_value: float
    threshold: float
    severity: str
    detected_at: datetime


__all__ = ["WindowState", "AggregatedMetric", "AnomalyResult"]
