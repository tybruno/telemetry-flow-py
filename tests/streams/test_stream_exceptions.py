"""Tests for stream exceptions."""

import pytest

from src.core.exceptions import TelemetryError
from src.streams.exceptions import (
    BackpressureError,
    ConsumerGroupError,
    StreamError,
)


class TestStreamExceptions:
    """Test suite for stream exception classes."""

    def test_stream_error_inherits_from_telemetry_error(self) -> None:
        """Test StreamError is subclass of TelemetryError."""
        assert issubclass(StreamError, TelemetryError)

    def test_stream_error_can_be_raised(self) -> None:
        """Test StreamError can be raised with message."""
        with pytest.raises(StreamError, match="test error"):
            raise StreamError("test error")

    def test_consumer_group_error_inherits_from_stream_error(self) -> None:
        """Test ConsumerGroupError is subclass of StreamError."""
        assert issubclass(ConsumerGroupError, StreamError)

    def test_consumer_group_error_can_be_raised(self) -> None:
        """Test ConsumerGroupError can be raised with message."""
        with pytest.raises(ConsumerGroupError, match="Group error"):
            raise ConsumerGroupError("Group error")

    def test_backpressure_error_inherits_from_stream_error(self) -> None:
        """Test BackpressureError is subclass of StreamError."""
        assert issubclass(BackpressureError, StreamError)

    def test_backpressure_error_can_be_raised(self) -> None:
        """Test BackpressureError can be raised with message."""
        with pytest.raises(BackpressureError, match="Backpressure exceeded"):
            raise BackpressureError("Backpressure exceeded")

    def test_exceptions_can_be_caught_as_stream_error(self) -> None:
        """Test all exceptions can be caught as StreamError."""
        for exc_class in [ConsumerGroupError, BackpressureError]:
            with pytest.raises(StreamError):
                raise exc_class("error")


__all__: list[str] = []
