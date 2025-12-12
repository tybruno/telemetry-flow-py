"""Detection-specific data models.

This module defines generic models for anomaly detection results. These
models are domain-agnostic and can represent anomalies detected in any
metric stream.

Classes:
    AnomalyResult: Generic anomaly detection result with severity
    AnomalySeverity: Severity classification for anomalies
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AnomalySeverity(Enum):
    """Severity levels for detected anomalies.

    Classifies anomalies by their criticality for proper alerting and
    response prioritization.

    Example:
        if threshold_exceeded > 2.0:
            severity = AnomalySeverity.CRITICAL
        elif threshold_exceeded > 1.5:
            severity = AnomalySeverity.HIGH
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, kw_only=True, slots=True)
class AnomalyResult:
    """Generic anomaly detection result.

    Domain-agnostic container for anomaly information detected from any
    metric stream. Includes severity, confidence, and contextual data.

    Attributes:
        is_anomaly: Whether an anomaly was detected
        severity: Classification of anomaly criticality
        confidence: Detection confidence score (0.0 to 1.0)
        description: Human-readable anomaly description
        detected_at: When anomaly was detected
        metric_value: The actual metric value that triggered detection
        threshold_value: The threshold that was exceeded (if applicable)
        context: Additional context data specific to detection strategy

    Example:
        result = AnomalyResult(
            is_anomaly=True,
            severity=AnomalySeverity.HIGH,
            confidence=0.95,
            description="CPU usage exceeded threshold: 95.0 > 80.0",
            detected_at=datetime.now(UTC),
            metric_value=95.0,
            threshold_value=80.0,
            context={"window_size": 60, "stddev": 5.2}
        )
    """
    is_anomaly: bool
    severity: AnomalySeverity
    confidence: float
    description: str
    detected_at: datetime
    metric_value: float
    threshold_value: float | None = None
    context: dict[str, float] | None = None


__all__ = ["AnomalyResult", "AnomalySeverity"]
