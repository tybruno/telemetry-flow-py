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

import logging as _log

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
        super().__init__()

        self._validate_threshold_params(thresholds, default_threshold)

        self._thresholds = thresholds.copy()
        self._default_threshold = default_threshold
        _log.info(
            "Threshold detector initialized: default=%f, custom_thresholds=%d",
            default_threshold,
            len(thresholds)
        )

    def _validate_threshold_params(
        self,
        thresholds: dict[str, float],
        default_threshold: float
    ) -> None:
        """Validate threshold configuration.

        Args:
            thresholds: Per-metric threshold values.
            default_threshold: Default threshold value.

        Raises:
            ValueError: If any threshold is negative.
        """
        if default_threshold < 0:
            error_message = "Default threshold cannot be negative: %f"
            _log.error(error_message, default_threshold)
            raise ValueError(error_message % default_threshold) from None

        for metric_name, threshold in thresholds.items():
            if threshold < 0:
                error_message = "Threshold for %s cannot be negative: %f"
                _log.error(error_message, metric_name, threshold)
                raise ValueError(error_message % (metric_name, threshold)) from None

    def is_anomaly(self, metric: WindowMetrics) -> bool:
        """Check if aggregated metric exceeds threshold.

        Compares metric value against configured threshold for that specific
        metric type, or default threshold if not configured.

        Args:
            metric: Aggregated metric to check.

        Returns:
            True if metric value exceeds threshold, False otherwise.

        Raises:
            ValueError: If metric is invalid or missing required fields.
        """
        self._validate_metric(metric)

        # Get metric-specific threshold or fall back to default
        threshold = self._thresholds.get(metric.metric_name, self._default_threshold)

        is_above_threshold = metric.average > threshold
        return is_above_threshold

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
        self._validate_metric(metric)

        # Get metric-specific threshold or fall back to default
        threshold = self._thresholds.get(metric.metric_name, self._default_threshold)
        actual_value = metric.average

        self._validate_is_anomaly(actual_value, threshold)

        excess_ratio = (actual_value - threshold) / threshold
        severity, confidence = self._calculate_severity(excess_ratio)

        description = self._format_description(metric, threshold, actual_value)

        anomaly_result = self._create_anomaly(
            metric=metric,
            severity=severity,
            description=description,
            confidence=confidence
        )

        from dataclasses import replace
        anomaly_with_threshold = replace(anomaly_result, threshold_value=threshold)

        return anomaly_with_threshold

    def _validate_is_anomaly(
        self,
        actual_value: float,
        threshold: float
    ) -> None:
        """Validate that metric represents an anomaly.

        Args:
            actual_value: Metric value.
            threshold: Threshold value.

        Raises:
            ValueError: If value doesn't exceed threshold.
        """
        if actual_value <= threshold:
            error_message = "Metric does not represent an anomaly: %f <= %f"
            _log.error(error_message, actual_value, threshold)
            raise ValueError(error_message % (actual_value, threshold)) from None

    def _calculate_severity(
        self,
        excess_ratio: float
    ) -> tuple[str, float]:
        """Calculate severity and confidence based on excess ratio.

        Args:
            excess_ratio: Ratio of excess over threshold.

        Returns:
            Tuple of (severity, confidence).
        """
        if excess_ratio > 0.5:
            severity_level = "critical"
            confidence_score = 1.0
        elif excess_ratio > 0.25:
            severity_level = "high"
            confidence_score = 0.95
        elif excess_ratio > 0.1:
            severity_level = "medium"
            confidence_score = 0.85
        else:
            severity_level = "low"
            confidence_score = 0.75

        return severity_level, confidence_score

    def detect(self, metric: WindowMetrics) -> AnomalyResult | None:
        """Detect anomalies in aggregated metric.

        Args:
            metric: Aggregated metric to analyze.

        Returns:
            AnomalyResult object if detected, None otherwise.

        Raises:
            ValueError: If metric is invalid.
        """
        if self.is_anomaly(metric):
            anomaly_result = self.create_anomaly_result(metric)
            return anomaly_result
        return None


__all__ = ["ThresholdDetector"]
