"""Processor service exceptions.

Classes:
    ProcessorError: Base processor exception.
    AggregationError: Aggregation failures.
    StateRecoveryError: State recovery failures.
    ConsumerError: Stream consumption errors.
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


__all__ = ["ProcessorError", "AggregationError", "StateRecoveryError", "ConsumerError"]
