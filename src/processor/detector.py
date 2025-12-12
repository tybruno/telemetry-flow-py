"""Anomaly detection for aggregated metrics.

Class:
    ThresholdDetector: Threshold-based anomaly detector.
"""
import logging

from src.processor.models import AggregatedMetric, AnomalyResult

_log = logging.getLogger(__name__)


class ThresholdDetector:
    """Threshold-based anomaly detector.
    
    Detects anomalies when metrics exceed configured thresholds.
    
    Attributes:
        _threshold: Threshold value for anomaly detection.
    """
    __slots__ = ("_threshold",)
    
    _threshold: float
    
    def __init__(self, *, threshold: float) -> None:
        """Initialize detector with threshold."""
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
