"""Tests for detection exceptions."""

import pytest

from src.core.exceptions import TelemetryError
from src.detection.exceptions import (
    DetectionError,
    DetectorNotConfiguredError,
    InvalidMetricError,
    InvalidThresholdError,
)


class TestDetectionExceptions:
    """Test suite for detection exception classes."""

    def test_detection_error_inherits_from_telemetry_error(self) -> None:
        """Test DetectionError is subclass of TelemetryError."""
        assert issubclass(DetectionError, TelemetryError)

    def test_detection_error_can_be_raised(self) -> None:
        """Test DetectionError can be raised with message."""
        with pytest.raises(DetectionError, match="test error"):
            raise DetectionError("test error")

    def test_invalid_threshold_error_inherits_from_detection_error(
        self,
    ) -> None:
        """Test InvalidThresholdError is subclass of DetectionError."""
        assert issubclass(InvalidThresholdError, DetectionError)

    def test_invalid_threshold_error_can_be_raised(self) -> None:
        """Test InvalidThresholdError can be raised with message."""
        with pytest.raises(InvalidThresholdError, match="Invalid threshold"):
            raise InvalidThresholdError("Invalid threshold")

    def test_invalid_metric_error_inherits_from_detection_error(
        self,
    ) -> None:
        """Test InvalidMetricError is subclass of DetectionError."""
        assert issubclass(InvalidMetricError, DetectionError)

    def test_invalid_metric_error_can_be_raised(self) -> None:
        """Test InvalidMetricError can be raised with message."""
        with pytest.raises(InvalidMetricError, match="Invalid metric"):
            raise InvalidMetricError("Invalid metric")

    def test_detector_not_configured_error_inherits_from_detection_error(
        self,
    ) -> None:
        """Test DetectorNotConfiguredError is subclass of DetectionError."""
        assert issubclass(DetectorNotConfiguredError, DetectionError)

    def test_detector_not_configured_error_can_be_raised(self) -> None:
        """Test DetectorNotConfiguredError can be raised with message."""
        with pytest.raises(DetectorNotConfiguredError, match="Not configured"):
            raise DetectorNotConfiguredError("Not configured")

    def test_exceptions_can_be_caught_as_detection_error(self) -> None:
        """Test all exceptions can be caught as DetectionError."""
        for exc_class in [
            InvalidThresholdError,
            InvalidMetricError,
            DetectorNotConfiguredError,
        ]:
            with pytest.raises(DetectionError):
                raise exc_class("error")


__all__: list[str] = []
