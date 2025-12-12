"""Stream consumer for telemetry events.

This module provides a robust stream consumer that handles the complete
message consumption pipeline including deserialization, validation,
backpressure management, error handling, and acknowledgment.

Classes:
    TelemetryConsumer: Consumes events with deserialization, validation,
        backpressure, error handling, and retries.
"""

from collections.abc import AsyncIterator

from src.consumers.backpressure import BackpressureManager
from src.consumers.deserializer import MessageDeserializer
from src.consumers.error_handler import ConsumerErrorHandler
from src.core.models import TelemetryEvent
from src.core.protocols import StreamProtocol


class TelemetryConsumer:
    """Robust consumer for telemetry events with full error handling.

    Handles the complete message consumption pipeline including:
    - Stream consumption with consumer groups
    - Message deserialization and validation
    - Backpressure management to prevent overload
    - Error handling with automatic retries
    - Message acknowledgment for at-least-once delivery

    Composes specialized components for each responsibility rather than
    implementing everything directly.

    Attributes:
        _stream: Stream protocol for reading messages.
        _deserializer: Deserializes raw data to TelemetryEvent.
        _error_handler: Handles errors and retries.
        _backpressure: Manages consumption rate limits.
        _stream_name: Name of the stream to consume from.
        _group_name: Consumer group for distributed processing.
        _consumer_name: Unique identifier for this consumer.

    Example:
        consumer = TelemetryConsumer(
            stream=redis_stream,
            deserializer=MessageDeserializer(),
            error_handler=ConsumerErrorHandler(max_retries=3),
            backpressure=BackpressureManager(max_pending=1000),
            stream_name="telemetry",
            group_name="processors",
            consumer_name="worker-01"
        )

        async for event in consumer.consume_events():
            await process(event)
    """

    __slots__ = (
        "_backpressure",
        "_consumer_name",
        "_deserializer",
        "_error_handler",
        "_group_name",
        "_stream",
        "_stream_name",
    )

    _stream: StreamProtocol
    _deserializer: MessageDeserializer
    _error_handler: ConsumerErrorHandler
    _backpressure: BackpressureManager
    _stream_name: str
    _group_name: str
    _consumer_name: str

    def __init__(
        self,
        *,
        stream: StreamProtocol,
        deserializer: MessageDeserializer,
        error_handler: ConsumerErrorHandler,
        backpressure: BackpressureManager,
        stream_name: str,
        group_name: str,
        consumer_name: str,
    ) -> None:
        """Initialize consumer with all dependencies.

        Args:
            stream: Stream protocol implementation.
            deserializer: Message deserializer.
            error_handler: Error handler with retry logic.
            backpressure: Backpressure manager.
            stream_name: Name of stream to consume from.
            group_name: Consumer group name.
            consumer_name: Unique name for this consumer.

        Raises:
            ValueError: If any required parameter is None or empty.
        """
        raise NotImplementedError

    async def consume_events(self) -> AsyncIterator[TelemetryEvent]:
        """Consume and deserialize telemetry events with error handling.

        Yields validated TelemetryEvent objects, handling deserialization
        errors, applying backpressure, and retrying transient failures.

        Yields:
            TelemetryEvent instances successfully parsed from stream.

        Raises:
            ConsumerError: If consumption fails critically.

        Example:
            async for event in consumer.consume_events():
                _log.info("Received: %s", event.device_id)
                await process_event(event)
        """
        raise NotImplementedError
        yield  # Make this a generator

    async def _process_message(
        self,
        *,
        message_id: str,
        data: dict[str, str],
    ) -> TelemetryEvent | None:
        """Process single message with deserialization and validation.

        Args:
            message_id: Stream message ID.
            data: Raw message data from stream.

        Returns:
            TelemetryEvent if successfully processed, None if should skip.

        Raises:
            DeserializationError: If message cannot be parsed.
        """
        raise NotImplementedError

    async def _acknowledge_message(self, message_id: str) -> None:
        """Acknowledge successful message processing.

        Args:
            message_id: ID of message to acknowledge.

        Raises:
            ConsumerError: If acknowledgment fails.
        """
        raise NotImplementedError


__all__ = ["TelemetryConsumer"]
