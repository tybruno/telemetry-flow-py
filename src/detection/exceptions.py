"""Detection-specific exceptions.

This module defines all exception types raised by the detection library,
allowing for both specific and broad error handling.

Classes:
    DetectionError: Base exception for all detection errors
    InvalidThresholdError: Raised when threshold configuration is invalid
    InvalidMetricError: Raised when metric data is invalid
    DetectorNotConfiguredError: Raised when detector lacks configuration

Example:
    Handling detection exceptions::

        try:
            result = await detector.detect(metrics)
        except InvalidThresholdError as e:
            _log.error("Invalid threshold config: %s", e)
        except DetectionError as e:
            _log.error("Detection error: %s", e)
"""
from src.core.exceptions import TelemetryError


class DetectionError(TelemetryError):
    """Base exception for all detection-related errors.

    All detection exceptions inherit from this base, allowing catch-all
    exception handling when needed.

    Example:
        try:
            await detector.process()
        except DetectionError as e:
            _log.error("Detection error occurred: %s", e)
    """


class InvalidThresholdError(DetectionError):
    """Raised when threshold configuration is invalid.

    Threshold values don't meet requirements (e.g., negative when
    positive required, out of valid range, wrong type).

    Example:
        if threshold < 0:
            raise InvalidThresholdError(
                f"Threshold must be non-negative, got {threshold}"
            )
    """


class InvalidMetricError(DetectionError):
    """Raised when metric data is invalid for detection.

    Metric values or metadata don't meet detection requirements.

    Example:
        if not isinstance(metric.value, (int, float)):
            raise InvalidMetricError(
                f"Expected numeric value, got {type(metric.value).__name__}"
            )
    """


class DetectorNotConfiguredError(DetectionError):
    """Raised when detector is used without proper configuration.

    Detector requires configuration (e.g., thresholds, model parameters)
    that has not been provided.

    Example:
        if not self._thresholds:
            raise DetectorNotConfiguredError(
                "Detector must be configured with thresholds"
            )
    """


__all__ = [
    "DetectionError",
    "DetectorNotConfiguredError",
    "InvalidMetricError",
    "InvalidThresholdError",
]
