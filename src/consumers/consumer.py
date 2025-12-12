"""Stream consumer for telemetry events.

This module provides a robust stream consumer that handles the complete
message consumption pipeline including deserialization, validation,
backpressure management, error handling, and acknowledgment.

Classes:
    TelemetryConsumer: Consumes events with deserialization, validation,
        backpressure, error handling, and retries.
"""

import logging as _log
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
        self._validate_dependency(stream, "stream")
        self._validate_dependency(deserializer, "deserializer")
        self._validate_dependency(error_handler, "error_handler")
        self._validate_dependency(backpressure, "backpressure")
        self._validate_string_param(stream_name, "stream_name")
        self._validate_string_param(group_name, "group_name")
        self._validate_string_param(consumer_name, "consumer_name")

        self._stream = stream
        self._deserializer = deserializer
        self._error_handler = error_handler
        self._backpressure = backpressure
        self._stream_name = stream_name
        self._group_name = group_name
        self._consumer_name = consumer_name

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
        _log.info(
            "Starting consumer: stream=%s, group=%s, consumer=%s",
            self._stream_name,
            self._group_name,
            self._consumer_name
        )

        await self._setup_consumer_group()

        async for message_id, data in await self._stream.consume(
            stream=self._stream_name,
            group=self._group_name,
            consumer_name=self._consumer_name,
        ):
            await self._handle_backpressure()

            event = await self._process_and_yield_event(message_id, data)
            if event:
                yield event

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
        _log.debug("Processing message_id=%s", message_id)

        async def deserialize_op(msg_data: dict[str, object]) -> TelemetryEvent:
            return self._deserializer.deserialize(msg_data)

        # Use error handler for deserialization with retry
        event: TelemetryEvent = await self._error_handler.with_retry(
            operation=deserialize_op,
            message_id=message_id,
            data=data
        )

        _log.debug(
            "Successfully processed message_id=%s: device=%s, metric=%s",
            message_id,
            event.device_id,
            event.metric_name
        )

        return event

    async def _acknowledge_message(self, message_id: str) -> None:
        """Acknowledge successful message processing.

        Args:
            message_id: ID of message to acknowledge.

        Raises:
            ConsumerError: If acknowledgment fails.
        """
        from src.consumers.exceptions import ConsumerError

        try:
            await self._stream.acknowledge(
                stream=self._stream_name,
                group=self._group_name,
                message_id=message_id
            )

            _log.debug("Acknowledged message_id=%s", message_id)

        except Exception as e:
            error_message = "Failed to acknowledge message_id=%s: %s"
            _log.error(error_message, message_id, str(e))
            raise ConsumerError(error_message % (message_id, str(e))) from e

    def _validate_dependency(self, dependency: object, name: str) -> None:
        """Validate that a dependency is not None.

        Args:
            dependency: Dependency object to validate.
            name: Name of dependency for error message.

        Raises:
            ValueError: If dependency is None.
        """
        if not dependency:
            error_message = "%s cannot be None"
            _log.error(error_message, name)
            raise ValueError(error_message % name) from None

    def _validate_string_param(self, value: str, name: str) -> None:
        """Validate that a string parameter is not empty.

        Args:
            value: String value to validate.
            name: Name of parameter for error message.

        Raises:
            ValueError: If value is None or empty.
        """
        if not value or not value.strip():
            error_message = "%s cannot be empty"
            _log.error(error_message, name)
            raise ValueError(error_message % name) from None

    async def _setup_consumer_group(self) -> None:
        """Create consumer group if it doesn't exist.

        Raises:
            ConsumerError: If group creation fails.
        """
        from src.consumers.exceptions import ConsumerError

        try:
            await self._stream.create_consumer_group(
                stream=self._stream_name,
                group=self._group_name
            )
        except Exception as e:
            _log.error("Failed to create consumer group: %s", str(e))
            raise ConsumerError("Consumer group creation failed") from e

    async def _handle_backpressure(self) -> None:
        """Check and wait for backpressure if needed."""
        if await self._backpressure.should_throttle():
            _log.warning("Backpressure detected, throttling consumption")
            await self._backpressure.wait()

    async def _process_and_yield_event(
        self,
        message_id: str,
        data: dict[str, str]
    ) -> TelemetryEvent | None:
        """Process message and handle acknowledgment.

        Args:
            message_id: Stream message ID.
            data: Raw message data.

        Returns:
            Processed event or None if processing failed.

        Raises:
            ConsumerError: If message acknowledgment fails.
        """
        try:
            event = await self._process_message(
                message_id=message_id,
                data=data
            )

            if event:
                await self._acknowledge_message(message_id)
                await self._backpressure.record_processed()
                return event

        except Exception as e:
            _log.error(
                "Failed to process message_id=%s: %s",
                message_id,
                str(e)
            )

        return None


__all__ = ["TelemetryConsumer"]
