"""Tests for Redis Streams implementation.

Tests the RedisStream class including connection, publishing, consuming,
acknowledgments, and consumer group management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.streams.exceptions import ConsumerGroupError, StreamError
from src.streams.redis_stream import RedisStream


class TestRedisStreamInitialization:
    """Tests for RedisStream initialization."""

    def test_init_with_valid_url(self) -> None:
        """Test initialization with valid Redis URL."""
        stream = RedisStream(url="redis://localhost:6379/0")
        
        assert stream._url == "redis://localhost:6379/0"
        assert stream._client is not None

    def test_init_with_empty_url_raises(self) -> None:
        """Test initialization with empty URL raises ValueError."""
        with pytest.raises(ValueError, match="Redis URL cannot be empty"):
            RedisStream(url="")

    def test_init_with_whitespace_url_raises(self) -> None:
        """Test initialization with whitespace URL raises ValueError."""
        with pytest.raises(ValueError, match="Redis URL cannot be empty"):
            RedisStream(url="   ")


class TestRedisStreamPublish:
    """Tests for Redis Stream publish method."""

    @pytest.mark.asyncio
    async def test_publish_success(self) -> None:
        """Test successful event publishing."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xadd = AsyncMock(return_value=b"1234567890-0")

        message_id = await stream.publish(
            stream="telemetry",
            data={"device_id": "router-01", "value": 85.5}
        )

        assert message_id == "1234567890-0"
        stream._client.xadd.assert_called_once_with(
            "telemetry",
            {"device_id": "router-01", "value": 85.5}
        )

    @pytest.mark.asyncio
    async def test_publish_with_empty_stream_raises(self) -> None:
        """Test publish with empty stream name raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Stream name cannot be empty"):
            await stream.publish(stream="", data={"key": "value"})

    @pytest.mark.asyncio
    async def test_publish_with_empty_data_raises(self) -> None:
        """Test publish with empty data raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Data cannot be empty"):
            await stream.publish(stream="telemetry", data={})

    @pytest.mark.asyncio
    async def test_publish_redis_error_raises_stream_error(self) -> None:
        """Test Redis error during publish raises StreamError."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xadd = AsyncMock(side_effect=Exception("Redis down"))

        with pytest.raises(StreamError, match="Failed to publish"):
            await stream.publish(
                stream="telemetry",
                data={"device_id": "router-01"}
            )


class TestRedisStreamConsumerGroup:
    """Tests for Redis Stream consumer group management."""

    @pytest.mark.asyncio
    async def test_create_consumer_group_success(self) -> None:
        """Test successful consumer group creation."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xgroup_create = AsyncMock()

        await stream.create_consumer_group(
            stream="telemetry",
            group="processors",
            start_id="$"
        )

        stream._client.xgroup_create.assert_called_once_with(
            "telemetry",
            "processors",
            "$",
            mkstream=True
        )

    @pytest.mark.asyncio
    async def test_create_consumer_group_already_exists(self) -> None:
        """Test consumer group creation when group already exists."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        
        # Simulate BUSYGROUP error from Redis
        error = Exception("BUSYGROUP Consumer Group name already exists")
        stream._client.xgroup_create = AsyncMock(side_effect=error)

        # Should not raise - group already exists is acceptable
        await stream.create_consumer_group(
            stream="telemetry",
            group="processors",
            start_id="$"
        )

    @pytest.mark.asyncio
    async def test_create_consumer_group_other_error_raises(self) -> None:
        """Test consumer group creation with non-BUSYGROUP error raises."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xgroup_create = AsyncMock(
            side_effect=Exception("Connection failed")
        )

        with pytest.raises(ConsumerGroupError, match="Failed to create consumer group"):
            await stream.create_consumer_group(
                stream="telemetry",
                group="processors",
                start_id="$"
            )

    @pytest.mark.asyncio
    async def test_create_consumer_group_with_empty_stream_raises(self) -> None:
        """Test consumer group creation with empty stream raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Stream name cannot be empty"):
            await stream.create_consumer_group(
                stream="",
                group="processors",
                start_id="$"
            )

    @pytest.mark.asyncio
    async def test_create_consumer_group_with_empty_group_raises(self) -> None:
        """Test consumer group creation with empty group raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Group name cannot be empty"):
            await stream.create_consumer_group(
                stream="telemetry",
                group="",
                start_id="$"
            )


class TestRedisStreamConsume:
    """Tests for Redis Stream consume method."""

    @pytest.mark.asyncio
    async def test_consume_yields_messages(self) -> None:
        """Test consume yields messages from stream."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        
        # Mock XREADGROUP responses
        stream._client.xreadgroup = AsyncMock(side_effect=[
            [[b"telemetry", [(b"1-0", {b"device_id": b"router-01", b"value": b"85.5"})]]],
            [[b"telemetry", [(b"1-1", {b"device_id": b"router-02", b"value": b"72.3"})]]],
            None  # End iteration
        ])

        messages = []
        async for msg_id, data in stream.consume(
            stream="telemetry",
            group="processors",
            consumer_name="worker-01"
        ):
            messages.append((msg_id, data))
            if len(messages) >= 2:
                break

        assert len(messages) == 2
        assert messages[0] == ("1-0", {"device_id": "router-01", "value": "85.5"})
        assert messages[1] == ("1-1", {"device_id": "router-02", "value": "72.3"})

    @pytest.mark.asyncio
    async def test_consume_with_empty_stream_raises(self) -> None:
        """Test consume with empty stream name raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        consumer_gen = stream.consume(
            stream="",
            group="processors",
            consumer_name="worker-01"
        )

        with pytest.raises(ValueError, match="Stream name cannot be empty"):
            await consumer_gen.__anext__()

    @pytest.mark.asyncio
    async def test_consume_with_empty_group_raises(self) -> None:
        """Test consume with empty group name raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        consumer_gen = stream.consume(
            stream="telemetry",
            group="",
            consumer_name="worker-01"
        )

        with pytest.raises(ValueError, match="Group name cannot be empty"):
            await consumer_gen.__anext__()

    @pytest.mark.asyncio
    async def test_consume_with_empty_consumer_raises(self) -> None:
        """Test consume with empty consumer name raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        consumer_gen = stream.consume(
            stream="telemetry",
            group="processors",
            consumer_name=""
        )

        with pytest.raises(ValueError, match="Consumer name cannot be empty"):
            await consumer_gen.__anext__()

    @pytest.mark.asyncio
    async def test_consume_redis_error_raises_stream_error(self) -> None:
        """Test Redis error during consume raises StreamError."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xreadgroup = AsyncMock(side_effect=Exception("Connection lost"))

        consumer_gen = stream.consume(
            stream="telemetry",
            group="processors",
            consumer_name="worker-01"
        )

        with pytest.raises(StreamError, match="Failed to consume"):
            await consumer_gen.__anext__()


class TestRedisStreamAcknowledge:
    """Tests for Redis Stream acknowledge method."""

    @pytest.mark.asyncio
    async def test_acknowledge_success(self) -> None:
        """Test successful message acknowledgment."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xack = AsyncMock(return_value=1)

        await stream.acknowledge(
            stream="telemetry",
            group="processors",
            message_id="1234567890-0"
        )

        stream._client.xack.assert_called_once_with(
            "telemetry",
            "processors",
            "1234567890-0"
        )

    @pytest.mark.asyncio
    async def test_acknowledge_with_empty_stream_raises(self) -> None:
        """Test acknowledge with empty stream raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Stream name cannot be empty"):
            await stream.acknowledge(
                stream="",
                group="processors",
                message_id="123-0"
            )

    @pytest.mark.asyncio
    async def test_acknowledge_with_empty_group_raises(self) -> None:
        """Test acknowledge with empty group raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Group name cannot be empty"):
            await stream.acknowledge(
                stream="telemetry",
                group="",
                message_id="123-0"
            )

    @pytest.mark.asyncio
    async def test_acknowledge_with_empty_message_id_raises(self) -> None:
        """Test acknowledge with empty message_id raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Message ID cannot be empty"):
            await stream.acknowledge(
                stream="telemetry",
                group="processors",
                message_id=""
            )

    @pytest.mark.asyncio
    async def test_acknowledge_redis_error_raises_stream_error(self) -> None:
        """Test Redis error during acknowledge raises StreamError."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xack = AsyncMock(side_effect=Exception("Connection error"))

        with pytest.raises(StreamError, match="Failed to acknowledge"):
            await stream.acknowledge(
                stream="telemetry",
                group="processors",
                message_id="123-0"
            )


class TestRedisStreamClose:
    """Tests for Redis Stream close method."""

    @pytest.mark.asyncio
    async def test_close_success(self) -> None:
        """Test successful stream connection close."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.close = AsyncMock()
        stream._client.connection_pool = MagicMock()
        stream._client.connection_pool.disconnect = AsyncMock()

        await stream.close()

        stream._client.close.assert_called_once()
        stream._client.connection_pool.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_with_error_logs_and_continues(self) -> None:
        """Test close with error logs but doesn't raise."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.close = AsyncMock(side_effect=Exception("Already closed"))

        # Should not raise - errors are logged
        await stream.close()
