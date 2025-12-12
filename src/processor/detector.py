"""Anomaly detection for aggregated metrics.

Class:
    ThresholdDetector: Metric-specific threshold-based detector.
"""

import logging

from src.processor.models import AggregatedMetric, AnomalyResult

_log = logging.getLogger(__name__)


class ThresholdDetector:
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

    __slots__ = ("_thresholds", "_default_threshold")

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

    def is_anomaly(self, metric: AggregatedMetric) -> bool:
        """Check if aggregated metric is anomalous.

        Args:
            metric: Aggregated metric to check.

        Returns:
            True if anomaly detected.
        """
        raise NotImplementedError

    def create_anomaly_result(
        self,
        metric: AggregatedMetric,
    ) -> AnomalyResult:
        """Create anomaly result from metric.

        Args:
            metric: Aggregated metric that triggered anomaly.

        Returns:
            AnomalyResult with details.
        """
        raise NotImplementedError


__all__ = ["ThresholdDetector"]
