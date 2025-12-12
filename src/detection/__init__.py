"""Reusable anomaly detection library.

This library provides generic anomaly detection capabilities that can detect
anomalies in any metric stream using various strategies. It is fully
domain-agnostic and extensible for different detection algorithms.

Classes:
    BaseDetector: Abstract base with shared detection utilities
    ThresholdDetector: Threshold-based detector implementation
    AnomalyResult: Generic anomaly detection result

Example:
    Basic detection setup::

        from detection import ThresholdDetector, AnomalyResult
        from aggregation import WindowMetrics

        detector = ThresholdDetector(
            thresholds={"cpu": 80.0, "memory": 90.0}
        )

        result = await detector.detect(window_metrics)
        if result and result.is_anomaly:
            print(f"Anomaly detected: {result.description}")
"""

from src.detection.base_detector import BaseDetector
from src.detection.models import AnomalyResult, AnomalySeverity
from src.detection.threshold import ThresholdDetector

__all__ = [
    "AnomalyResult",
    "AnomalySeverity",
    "BaseDetector",
    "ThresholdDetector",
]
