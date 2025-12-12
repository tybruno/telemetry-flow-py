"""Threshold-based anomaly detection for aggregated metrics.

This module provides threshold-based anomaly detection with metric-specific
thresholds and fallback defaults. Different metrics can have different
sensitivity levels.

Classes:
    ThresholdDetector: Metric-specific threshold-based detector.

Example:
    Basic threshold detection usage::

        from detection import ThresholdDetector
        from aggregation.models import WindowMetrics

        detector = ThresholdDetector(
            thresholds={
                "cpu_utilization": 90.0,
                "bandwidth_utilization": 95.0,
                "error_rate": 1.0,
            },
            default_threshold=80.0
        )

        metric = WindowMetrics(...)
        if detector.is_anomaly(metric):
            result = detector.create_anomaly_result(metric)
            print(f"Anomaly: {result.description}")
"""


from src.aggregation.models import WindowMetrics
from src.detection.base_detector import BaseDetector
from src.detection.models import AnomalyResult


class ThresholdDetector(BaseDetector):
    """Metric-specific threshold-based anomaly detector.

    Compares metrics against per-metric thresholds with fallback
    default. Different metrics can have different sensitivities.

    Attributes:
        _thresholds: Metric-specific threshold values.
        _default_threshold: Fallback for unconfigured metrics.

    Example:
        detector = ThresholdDetector(
            thresholds={
                "bandwidth_utilization": 90.0,
                "error_rate": 1.0,
                "packet_loss": 0.5,
            },
            default_threshold=80.0
        )

        if detector.is_anomaly(metric):
            result = detector.create_anomaly_result(metric)
    """

    __slots__ = ("_default_threshold", "_thresholds")

    _thresholds: dict[str, float]
    _default_threshold: float

    def __init__(
        self,
        *,
        thresholds: dict[str, float],
        default_threshold: float = 80.0,
    ) -> None:
        """Initialize with metric-specific thresholds.

        Args:
            thresholds: Per-metric threshold values.
            default_threshold: Fallback for unconfigured metrics.

        Raises:
            ValueError: If thresholds or default is negative.
        """
        raise NotImplementedError

    def is_anomaly(self, metric: WindowMetrics) -> bool:
        """Check if aggregated metric exceeds threshold.

        Compares metric value against configured threshold for that metric
        type, or default threshold if not configured.

        Args:
            metric: Aggregated metric to check.

        Returns:
            True if metric value exceeds threshold, False otherwise.

        Raises:
            ValueError: If metric is invalid or missing required fields.
        """
        raise NotImplementedError

    def create_anomaly_result(
        self,
        metric: WindowMetrics,
    ) -> AnomalyResult:
        """Create detailed anomaly result from metric.

        Generates AnomalyResult with severity, description, and confidence
        based on how much the metric exceeded the threshold.

        Args:
            metric: Aggregated metric that triggered anomaly.

        Returns:
            AnomalyResult with severity, description, and confidence.

        Raises:
            ValueError: If metric is invalid or does not represent an anomaly.
        """
        raise NotImplementedError


__all__ = ["ThresholdDetector"]
