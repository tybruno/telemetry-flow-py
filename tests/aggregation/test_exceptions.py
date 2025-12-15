"""Tests for aggregation exceptions."""

import pytest

from src.aggregation.exceptions import (
    AggregationError,
    InvalidMetricError,
    StateError,
    WindowError,
)
from src.core.exceptions import TelemetryError


class TestAggregationExceptions:
    """Test suite for aggregation exception classes."""

    def test_aggregation_error_inherits_from_telemetry_error(self) -> None:
        """Test AggregationError is subclass of TelemetryError."""
        assert issubclass(AggregationError, TelemetryError)

    def test_aggregation_error_can_be_raised(self) -> None:
        """Test AggregationError can be raised with message."""
        with pytest.raises(AggregationError, match="test error"):
            raise AggregationError("test error")

    def test_window_error_inherits_from_aggregation_error(self) -> None:
        """Test WindowError is subclass of AggregationError."""
        assert issubclass(WindowError, AggregationError)

    def test_window_error_can_be_raised(self) -> None:
        """Test WindowError can be raised with message."""
        with pytest.raises(WindowError, match="Invalid window"):
            raise WindowError("Invalid window")

    def test_invalid_metric_error_inherits_from_aggregation_error(
        self,
    ) -> None:
        """Test InvalidMetricError is subclass of AggregationError."""
        assert issubclass(InvalidMetricError, AggregationError)

    def test_invalid_metric_error_can_be_raised(self) -> None:
        """Test InvalidMetricError can be raised with message."""
        with pytest.raises(InvalidMetricError, match="Invalid metric"):
            raise InvalidMetricError("Invalid metric")

    def test_state_error_inherits_from_aggregation_error(self) -> None:
        """Test StateError is subclass of AggregationError."""
        assert issubclass(StateError, AggregationError)

    def test_state_error_can_be_raised(self) -> None:
        """Test StateError can be raised with message."""
        with pytest.raises(StateError, match="State error"):
            raise StateError("State error")

    def test_exceptions_can_be_caught_as_aggregation_error(self) -> None:
        """Test all exceptions can be caught as AggregationError."""
        for exc_class in [WindowError, InvalidMetricError, StateError]:
            with pytest.raises(AggregationError):
                raise exc_class("error")


__all__: list[str] = []
