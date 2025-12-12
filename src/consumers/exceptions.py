"""Consumer-specific exceptions.

This module defines all exception types raised by the consumer library,
forming a hierarchy that allows for both specific and broad error handling.

Classes:
    ConsumerError: Base exception for all consumer errors
    DeserializationError: Raised when message deserialization fails
    ValidationError: Raised when message validation fails
    RetryExhaustedError: Raised when max retries exceeded
    BackpressureError: Raised when backpressure limits reached

Example:
    Handling consumer exceptions::
    
        try:
            message = await consumer.consume_next()
        except DeserializationError as e:
            _log.error("Failed to parse message: %s", e)
        except ConsumerError as e:
            _log.error("Consumer error: %s", e)
"""
from src.core.exceptions import TelemetryError


class ConsumerError(TelemetryError):
    """Base exception for all consumer-related errors.
    
    All consumer exceptions inherit from this base, allowing catch-all
    exception handling when needed.
    
    Example:
        try:
            await consumer.process()
        except ConsumerError as e:
            _log.error("Consumer error occurred: %s", e)
    """


class DeserializationError(ConsumerError):
    """Raised when message deserialization fails.
    
    Indicates message data could not be parsed into expected format.
    Usually a permanent error that requires investigation.
    
    Example:
        if not isinstance(data, dict):
            raise DeserializationError(
                f"Expected dict, got {type(data).__name__}"
            )
    """


class ValidationError(ConsumerError):
    """Raised when deserialized message fails validation.
    
    Message was parsed but doesn't meet required schema or constraints.
    Usually a permanent error indicating bad data.
    
    Example:
        if "device_id" not in event:
            raise ValidationError("Missing required field: device_id")
    """


class RetryExhaustedError(ConsumerError):
    """Raised when maximum retry attempts have been exceeded.
    
    Message processing failed repeatedly despite retries. Usually
    indicates a persistent issue requiring manual intervention.
    
    Attributes:
        message_id: ID of the message that failed
        retry_count: Number of retries attempted
    
    Example:
        if attempt > max_retries:
            raise RetryExhaustedError(
                f"Max retries ({max_retries}) exceeded for message {msg_id}"
            )
    """


class BackpressureError(ConsumerError):
    """Raised when backpressure thresholds are exceeded.
    
    System is overloaded and cannot process messages at current rate.
    Indicates need for throttling or scaling.
    
    Example:
        if processing_rate > max_rate:
            raise BackpressureError(
                f"Processing rate {processing_rate} exceeds maximum {max_rate}"
            )
    """


__all__ = [
    "ConsumerError",
    "DeserializationError",
    "ValidationError",
    "RetryExhaustedError",
    "BackpressureError",
]
