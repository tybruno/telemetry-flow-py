"""Tests for TelemetryConsumer edge cases and validation."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.consumers.backpressure import BackpressureManager
from src.consumers.consumer import TelemetryConsumer
from src.consumers.deserializer import MessageDeserializer
from src.consumers.error_handler import ConsumerErrorHandler
from src.consumers.exceptions import ConsumerError


class TestTelemetryConsumerValidation:
    """Tests for consumer parameter validation."""

    def test_consumer_rejects_none_stream(self) -> None:
        """Test consumer raises ValueError for None stream."""
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        backpressure = BackpressureManager(max_rate=100)

        with pytest.raises(ValueError, match="stream cannot be None"):
            TelemetryConsumer(
                stream=None,  # type: ignore
                deserializer=deserializer,
                error_handler=error_handler,
                backpressure=backpressure,
                stream_name="test-stream",
                group_name="test-group",
                consumer_name="test-consumer",
            )

    def test_consumer_rejects_none_deserializer(self) -> None:
        """Test consumer raises ValueError for None deserializer."""
        mock_stream = MagicMock()
        error_handler = ConsumerErrorHandler(max_retries=3)
        backpressure = BackpressureManager(max_rate=100)

        with pytest.raises(ValueError, match="deserializer cannot be None"):
            TelemetryConsumer(
                stream=mock_stream,
                deserializer=None,  # type: ignore
                error_handler=error_handler,
                backpressure=backpressure,
                stream_name="test-stream",
                group_name="test-group",
                consumer_name="test-consumer",
            )

    def test_consumer_rejects_none_error_handler(self) -> None:
        """Test consumer raises ValueError for None error_handler."""
        mock_stream = MagicMock()
        deserializer = MessageDeserializer()
        backpressure = BackpressureManager(max_rate=100)

        with pytest.raises(ValueError, match="error_handler cannot be None"):
            TelemetryConsumer(
                stream=mock_stream,
                deserializer=deserializer,
                error_handler=None,  # type: ignore
                backpressure=backpressure,
                stream_name="test-stream",
                group_name="test-group",
                consumer_name="test-consumer",
            )

    def test_consumer_rejects_none_backpressure(self) -> None:
        """Test consumer raises ValueError for None backpressure."""
        mock_stream = MagicMock()
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)

        with pytest.raises(ValueError, match="backpressure cannot be None"):
            TelemetryConsumer(
                stream=mock_stream,
                deserializer=deserializer,
                error_handler=error_handler,
                backpressure=None,  # type: ignore
                stream_name="test-stream",
                group_name="test-group",
                consumer_name="test-consumer",
            )

    def test_consumer_rejects_empty_stream_name(self) -> None:
        """Test consumer raises ValueError for empty stream_name."""
        mock_stream = MagicMock()
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        backpressure = BackpressureManager(max_rate=100)

        with pytest.raises(ValueError, match="stream_name cannot be empty"):
            TelemetryConsumer(
                stream=mock_stream,
                deserializer=deserializer,
                error_handler=error_handler,
                backpressure=backpressure,
                stream_name="",
                group_name="test-group",
                consumer_name="test-consumer",
            )

    def test_consumer_rejects_empty_group_name(self) -> None:
        """Test consumer raises ValueError for empty group_name."""
        mock_stream = MagicMock()
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        backpressure = BackpressureManager(max_rate=100)

        with pytest.raises(ValueError, match="group_name cannot be empty"):
            TelemetryConsumer(
                stream=mock_stream,
                deserializer=deserializer,
                error_handler=error_handler,
                backpressure=backpressure,
                stream_name="test-stream",
                group_name="",
                consumer_name="test-consumer",
            )

    def test_consumer_rejects_empty_consumer_name(self) -> None:
        """Test consumer raises ValueError for empty consumer_name."""
        mock_stream = MagicMock()
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        backpressure = BackpressureManager(max_rate=100)

        with pytest.raises(ValueError, match="consumer_name cannot be empty"):
            TelemetryConsumer(
                stream=mock_stream,
                deserializer=deserializer,
                error_handler=error_handler,
                backpressure=backpressure,
                stream_name="test-stream",
                group_name="test-group",
                consumer_name="",
            )


class TestTelemetryConsumerAcknowledge:
    """Tests for message acknowledgment."""

    @pytest.mark.asyncio
    async def test_acknowledge_message_success(self) -> None:
        """Test successful message acknowledgment."""
        mock_stream = AsyncMock()
        mock_stream.acknowledge = AsyncMock()
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        backpressure = BackpressureManager(max_rate=100)

        consumer = TelemetryConsumer(
            stream=mock_stream,
            deserializer=deserializer,
            error_handler=error_handler,
            backpressure=backpressure,
            stream_name="test-stream",
            group_name="test-group",
            consumer_name="test-consumer",
        )

        await consumer._acknowledge_message("1234567890-0")

        mock_stream.acknowledge.assert_called_once_with(
            stream="test-stream", group="test-group", message_id="1234567890-0"
        )

    @pytest.mark.asyncio
    async def test_acknowledge_message_failure(self) -> None:
        """Test acknowledge raises ConsumerError on failure."""
        mock_stream = AsyncMock()
        mock_stream.acknowledge = AsyncMock(side_effect=Exception("Redis error"))
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        backpressure = BackpressureManager(max_rate=100)

        consumer = TelemetryConsumer(
            stream=mock_stream,
            deserializer=deserializer,
            error_handler=error_handler,
            backpressure=backpressure,
            stream_name="test-stream",
            group_name="test-group",
            consumer_name="test-consumer",
        )

        with pytest.raises(ConsumerError, match="Failed to acknowledge"):
            await consumer._acknowledge_message("1234567890-0")


class TestTelemetryConsumerSetup:
    """Tests for consumer group setup."""

    @pytest.mark.asyncio
    async def test_setup_consumer_group_calls_stream(self) -> None:
        """Test _setup_consumer_group calls stream.create_consumer_group."""
        mock_stream = AsyncMock()
        mock_stream.create_consumer_group = AsyncMock()
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        backpressure = BackpressureManager(max_rate=100)

        consumer = TelemetryConsumer(
            stream=mock_stream,
            deserializer=deserializer,
            error_handler=error_handler,
            backpressure=backpressure,
            stream_name="test-stream",
            group_name="test-group",
            consumer_name="test-consumer",
        )

        await consumer._setup_consumer_group()

        mock_stream.create_consumer_group.assert_called_once_with(
            stream="test-stream", group="test-group"
        )

    @pytest.mark.asyncio
    async def test_setup_consumer_group_failure(self) -> None:
        """Test _setup_consumer_group raises ConsumerError on failure."""
        mock_stream = AsyncMock()
        error_msg = "Stream error"
        mock_stream.create_consumer_group = AsyncMock(side_effect=Exception(error_msg))
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        backpressure = BackpressureManager(max_rate=100)

        consumer = TelemetryConsumer(
            stream=mock_stream,
            deserializer=deserializer,
            error_handler=error_handler,
            backpressure=backpressure,
            stream_name="test-stream",
            group_name="test-group",
            consumer_name="test-consumer",
        )

        with pytest.raises(ConsumerError, match="Consumer group creation failed"):
            await consumer._setup_consumer_group()


class TestTelemetryConsumerBackpressure:
    """Tests for backpressure handling."""

    @pytest.mark.asyncio
    async def test_handle_backpressure_when_throttled(self) -> None:
        """Test _handle_backpressure waits when throttling needed."""
        mock_stream = MagicMock()
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        mock_backpressure = AsyncMock()
        mock_backpressure.should_throttle = AsyncMock(return_value=True)
        mock_backpressure.wait = AsyncMock()

        consumer = TelemetryConsumer(
            stream=mock_stream,
            deserializer=deserializer,
            error_handler=error_handler,
            backpressure=mock_backpressure,  # type: ignore
            stream_name="test-stream",
            group_name="test-group",
            consumer_name="test-consumer",
        )

        await consumer._handle_backpressure()

        mock_backpressure.should_throttle.assert_called_once()
        mock_backpressure.wait.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_backpressure_when_not_throttled(self) -> None:
        """Test _handle_backpressure does not wait when no throttling."""
        mock_stream = MagicMock()
        deserializer = MessageDeserializer()
        error_handler = ConsumerErrorHandler(max_retries=3)
        mock_backpressure = AsyncMock()
        mock_backpressure.should_throttle = AsyncMock(return_value=False)
        mock_backpressure.wait = AsyncMock()

        consumer = TelemetryConsumer(
            stream=mock_stream,
            deserializer=deserializer,
            error_handler=error_handler,
            backpressure=mock_backpressure,  # type: ignore
            stream_name="test-stream",
            group_name="test-group",
            consumer_name="test-consumer",
        )

        await consumer._handle_backpressure()

        mock_backpressure.should_throttle.assert_called_once()
        mock_backpressure.wait.assert_not_called()


__all__ = [
    "TestTelemetryConsumerValidation",
    "TestTelemetryConsumerAcknowledge",
    "TestTelemetryConsumerSetup",
    "TestTelemetryConsumerBackpressure",
]
