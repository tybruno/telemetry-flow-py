"""Processor service-specific exceptions.

This module defines exceptions specific to the processor service orchestration
logic. Library-specific exceptions (consumer, aggregation, detection) are
defined in their respective library packages.

Classes:
    ProcessorError: Base processor exception
    OrchestrationError: Worker orchestration failures
    StateRecoveryError: State recovery failures
    TelemetryProcessingError: Telemetry-specific processing errors

Example:
    Handling processor exceptions::
    
        try:
            await worker.process_event(event)
        except TelemetryProcessingError as e:
            _log.error("Failed to process telemetry: %s", e)
        except ProcessorError as e:
            _log.error("Processor error: %s", e)
"""

from src.core.exceptions import TelemetryError


class ProcessorError(TelemetryError):
    """Base exception for processor service errors.
    
    All processor service exceptions inherit from this base.
    
    Example:
        try:
            await processor.run()
        except ProcessorError as e:
            _log.error("Processor error occurred: %s", e)
    """


class OrchestrationError(ProcessorError):
    """Worker orchestration failure.
    
    Raised when coordinating between consumer, aggregation, detection,
    storage, and alerting components fails.
    
    Example:
        if not all([consumer, aggregator, detector]):
            raise OrchestrationError(
                "Worker requires all components to be initialized"
            )
    """


class StateRecoveryError(ProcessorError):
    """Worker state recovery failure.
    
    Raised when worker cannot recover its state after restart or failure,
    preventing it from resuming processing safely.
    
    Example:
        if not recovered_state:
            raise StateRecoveryError(
                f"Failed to recover state for worker {worker_id}"
            )
    """


class TelemetryProcessingError(ProcessorError):
    """Telemetry-specific processing error.
    
    Raised when telemetry event processing fails in a way specific to
    the telemetry domain (e.g., invalid device ID format, unknown metric).
    
    Example:
        if not is_valid_device_id(event.device_id):
            raise TelemetryProcessingError(
                f"Invalid device ID format: {event.device_id}"
            )
    """


__all__ = [
    "ProcessorError",
    "OrchestrationError",
    "StateRecoveryError",
    "TelemetryProcessingError",
]
