"""Processor service exceptions.

Classes:
    ProcessorError: Base processor exception.
    AggregationError: Aggregation failures.
    StateRecoveryError: State recovery failures.
    ConsumerError: Stream consumption errors.
    DeserializationError: Message deserialization failures.
    MaxRetriesExceededError: Retry limit exceeded errors.
"""

from src.core.exceptions import TelemetryError


class ProcessorError(TelemetryError):
    """Base exception for processor service errors."""


class AggregationError(ProcessorError):
    """Aggregation calculation failure."""


class StateRecoveryError(ProcessorError):
    """Worker state recovery failure."""


class ConsumerError(ProcessorError):
    """Stream consumption error."""


class DeserializationError(ProcessorError):
    """Message deserialization failure.

    Raised when raw stream data cannot be parsed into TelemetryEvent.
    """


class MaxRetriesExceededError(ProcessorError):
    """Maximum retry attempts exceeded.

    Raised when a message fails processing after all retry attempts.
    """


__all__ = [
    "ProcessorError",
    "AggregationError",
    "StateRecoveryError",
    "ConsumerError",
    "DeserializationError",
    "MaxRetriesExceededError",
]
