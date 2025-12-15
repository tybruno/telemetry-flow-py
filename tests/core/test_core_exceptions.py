"""Tests for core exceptions."""

import pytest

from src.core.exceptions import ConfigurationError, TelemetryError, ValidationError


class TestTelemetryError:
    """Test suite for TelemetryError exception."""

    def test_telemetry_error_is_exception(self) -> None:
        """Test TelemetryError inherits from Exception."""
        error = TelemetryError("Test error")
        assert isinstance(error, Exception)

    def test_telemetry_error_with_message(self) -> None:
        """Test TelemetryError stores message."""
        error_message = "System failure"
        error = TelemetryError(error_message)
        assert str(error) == error_message

    def test_telemetry_error_can_be_raised(self) -> None:
        """Test TelemetryError can be raised and caught."""
        with pytest.raises(TelemetryError, match="Test"):
            raise TelemetryError("Test")


class TestConfigurationError:
    """Test suite for ConfigurationError exception."""

    def test_configuration_error_is_telemetry_error(self) -> None:
        """Test ConfigurationError inherits from TelemetryError."""
        error = ConfigurationError("Config failed")
        assert isinstance(error, TelemetryError)
        assert isinstance(error, Exception)

    def test_configuration_error_with_message(self) -> None:
        """Test ConfigurationError stores message."""
        error_message = "Invalid configuration file"
        error = ConfigurationError(error_message)
        assert str(error) == error_message

    def test_configuration_error_can_be_raised(self) -> None:
        """Test ConfigurationError can be raised and caught."""
        with pytest.raises(ConfigurationError, match="Config"):
            raise ConfigurationError("Config error")

    def test_configuration_error_caught_as_telemetry_error(self) -> None:
        """Test ConfigurationError can be caught as TelemetryError."""
        with pytest.raises(TelemetryError):
            raise ConfigurationError("Config error")


class TestValidationError:
    """Test suite for ValidationError exception."""

    def test_validation_error_is_telemetry_error(self) -> None:
        """Test ValidationError inherits from TelemetryError."""
        error = ValidationError("Validation failed")
        assert isinstance(error, TelemetryError)
        assert isinstance(error, Exception)

    def test_validation_error_with_message(self) -> None:
        """Test ValidationError stores message."""
        error_message = "Invalid field value"
        error = ValidationError(error_message)
        assert str(error) == error_message

    def test_validation_error_can_be_raised(self) -> None:
        """Test ValidationError can be raised and caught."""
        with pytest.raises(ValidationError, match="Invalid"):
            raise ValidationError("Invalid data")

    def test_validation_error_caught_as_telemetry_error(self) -> None:
        """Test ValidationError can be caught as TelemetryError."""
        with pytest.raises(TelemetryError):
            raise ValidationError("Validation failed")


__all__: list[str] = []
