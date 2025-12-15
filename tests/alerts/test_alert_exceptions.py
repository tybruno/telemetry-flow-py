"""Tests for alert exceptions."""

import pytest

from src.alerts.exceptions import AlertDeliveryError, AlertError
from src.core.exceptions import TelemetryError


class TestAlertError:
    """Test suite for AlertError exception."""

    def test_alert_error_is_telemetry_error(self) -> None:
        """Test AlertError inherits from TelemetryError."""
        error = AlertError("Test error")
        assert isinstance(error, TelemetryError)
        assert isinstance(error, Exception)

    def test_alert_error_with_message(self) -> None:
        """Test AlertError stores message."""
        error_message = "Alert system failure"
        error = AlertError(error_message)
        assert str(error) == error_message

    def test_alert_error_can_be_raised(self) -> None:
        """Test AlertError can be raised and caught."""
        with pytest.raises(AlertError, match="Test"):
            raise AlertError("Test")


class TestAlertDeliveryError:
    """Test suite for AlertDeliveryError exception."""

    def test_delivery_error_is_alert_error(self) -> None:
        """Test AlertDeliveryError inherits from AlertError."""
        error = AlertDeliveryError("Delivery failed")
        assert isinstance(error, AlertError)
        assert isinstance(error, TelemetryError)
        assert isinstance(error, Exception)

    def test_delivery_error_with_message(self) -> None:
        """Test AlertDeliveryError stores message."""
        error_message = "Failed to send alert to endpoint"
        error = AlertDeliveryError(error_message)
        assert str(error) == error_message

    def test_delivery_error_can_be_raised(self) -> None:
        """Test AlertDeliveryError can be raised and caught."""
        with pytest.raises(AlertDeliveryError, match="Failed"):
            raise AlertDeliveryError("Failed to deliver")

    def test_delivery_error_caught_as_alert_error(self) -> None:
        """Test AlertDeliveryError can be caught as AlertError."""
        with pytest.raises(AlertError):
            raise AlertDeliveryError("Delivery failed")

    def test_delivery_error_caught_as_telemetry_error(self) -> None:
        """Test AlertDeliveryError can be caught as TelemetryError."""
        with pytest.raises(TelemetryError):
            raise AlertDeliveryError("Delivery failed")


__all__: list[str] = []
