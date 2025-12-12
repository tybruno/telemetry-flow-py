"""Stream infrastructure exceptions.

Classes:
    StreamError: Base stream exception.
    ConsumerGroupError: Consumer group operation failures.
    BackpressureError: Backpressure threshold exceeded.
"""

from src.core.exceptions import TelemetryError


class StreamError(TelemetryError):
    """Base exception for stream operations."""


class ConsumerGroupError(StreamError):
    """Consumer group operation failed."""


class BackpressureError(StreamError):
    """Backpressure threshold exceeded."""


__all__ = ["BackpressureError", "ConsumerGroupError", "StreamError"]
