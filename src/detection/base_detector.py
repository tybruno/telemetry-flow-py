"""Base detector implementation with shared utilities.

This module provides an abstract base class for anomaly detector
implementations, offering shared validation and formatting functionality
while allowing concrete classes to implement protocol-specific detection logic.

Classes:
    BaseDetector: Abstract base class for detector implementations.
"""

from abc import ABC, abstractmethod

from src.aggregation.models import WindowMetrics
from src.detection.models import AnomalyResult


class BaseDetector(ABC):
    """Abstract base class for anomaly detector implementations.

    Provides shared validation and formatting utilities for all detector
    implementations while enforcing core detection operations through
    abstract methods. Concrete classes inherit from this base and also
    satisfy the DetectorProtocol contract.

    This hybrid approach combines:
    - Protocol: Defines contract for duck typing and flexible algorithms
    - ABC: Provides shared implementation for validation and formatting

    Example:
        class ThresholdDetector(BaseDetector):
            def detect(self, metric: WindowMetrics) -> AnomalyResult | None:
                self._validate_metric(metric)
                # Threshold-specific detection logic
                if metric.value > threshold:
                    return self._create_anomaly(metric, ...)
                return None
    """

    def __init__(self) -> None:
        """Initialize base detector."""
        raise NotImplementedError

    @abstractmethod
    def detect(self, metric: WindowMetrics) -> AnomalyResult | None:
        """Detect anomalies in aggregated metric.

        Must be implemented by concrete classes to provide specific
        detection algorithms (threshold, statistical, ML-based, etc.).

        Args:
            metric: Aggregated metric to analyze.

        Returns:
            AnomalyResult object if detected, None otherwise.

        Raises:
            ValueError: If metric is invalid.
        """
        raise NotImplementedError

    def _validate_metric(self, metric: WindowMetrics) -> None:
        """Validate aggregated metric for detection.

        Shared validation logic used by all detector implementations.
        Ensures metric has required fields and valid values.

        Args:
            metric: Metric to validate.

        Raises:
            ValueError: If metric is invalid or incomplete.

        Example:
            self._validate_metric(metric)  # Before detection
        """
        raise NotImplementedError

    def _create_anomaly(
        self,
        metric: WindowMetrics,
        severity: str,
        description: str,
        confidence: float = 1.0,
    ) -> AnomalyResult:
        """Create anomaly object with consistent formatting.

        Shared utility for creating anomaly objects with proper
        formatting and metadata. Ensures consistent anomaly structure
        across all detector types.

        Args:
            metric: Metric that triggered the anomaly.
            severity: Anomaly severity level.
            description: Human-readable anomaly description.
            confidence: Detection confidence score (0.0-1.0).

        Returns:
            Formatted AnomalyResult object.

        Example:
            anomaly = self._create_anomaly(
                metric=metric,
                severity="high",
                description="Bandwidth exceeded threshold",
                confidence=0.95
            )
        """
        raise NotImplementedError

    def _format_description(
        self, metric: WindowMetrics, threshold: float, actual_value: float
    ) -> str:
        """Format anomaly description with metric details.

        Shared utility for creating human-readable anomaly descriptions
        with consistent formatting across detector types.

        Args:
            metric: Metric being analyzed.
            threshold: Threshold or expected value.
            actual_value: Actual measured value.

        Returns:
            Formatted description string.

        Example:
            desc = self._format_description(
                metric=metric,
                threshold=90.0,
                actual_value=95.5
            )
            # "Bandwidth utilization (95.5%) exceeded threshold (90.0%)"
        """
        raise NotImplementedError


__all__ = ["BaseDetector"]
