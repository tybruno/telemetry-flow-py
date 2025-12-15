"""Tests for RedisStream initialization and error handling."""

from unittest.mock import AsyncMock

import pytest

from src.streams.exceptions import StreamError
from src.streams.redis_stream import RedisStream


class TestRedisStreamInitialization:
    """Tests for RedisStream initialization."""

    def test_init_success(self) -> None:
        """Test successful initialization."""
        stream = RedisStream(url="redis://localhost:6379/0")

        assert stream._url == "redis://localhost:6379/0"
        assert stream._client is not None

    def test_init_empty_url(self) -> None:
        """Test initialization with empty URL."""
        with pytest.raises(ValueError, match="Redis URL cannot be empty"):
            RedisStream(url="")

    def test_init_whitespace_url(self) -> None:
        """Test initialization with whitespace-only URL."""
        with pytest.raises(ValueError, match="Redis URL cannot be empty"):
            RedisStream(url="   ")


class TestRedisStreamPublish:
    """Tests for publish operations."""

    @pytest.mark.asyncio
    async def test_publish_success(self) -> None:
        """Test successful publish."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xadd = AsyncMock(return_value="1234567890-0")

        result = await stream.publish(
            stream="telemetry", data={"device_id": "device-01"}
        )

        assert result == "1234567890-0"
        stream._client.xadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_empty_key_raises(self) -> None:
        """Test publish with empty stream key."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()

        with pytest.raises(ValueError, match="Stream name cannot be empty"):
            await stream.publish(stream="", data={"device_id": "device-01"})

    @pytest.mark.asyncio
    async def test_publish_empty_data_raises(self) -> None:
        """Test publish with empty data dict."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()

        with pytest.raises(ValueError, match="Data cannot be empty"):
            await stream.publish(stream="telemetry", data={})

    @pytest.mark.asyncio
    async def test_publish_redis_error_raises(self) -> None:
        """Test publish with Redis error."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xadd = AsyncMock(side_effect=Exception("Redis error"))

        with pytest.raises(StreamError, match="Failed to publish"):
            await stream.publish(stream="telemetry", data={"device_id": "device-01"})


class TestRedisStreamCreateConsumerGroup:
    """Tests for consumer group creation."""

    @pytest.mark.asyncio
    async def test_create_consumer_group_success(self) -> None:
        """Test successful consumer group creation."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xgroup_create = AsyncMock()

        await stream.create_consumer_group(stream="telemetry", group="processors")

        stream._client.xgroup_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_consumer_group_empty_stream_raises(self) -> None:
        """Test create_consumer_group with empty stream."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Stream name cannot be empty"):
            await stream.create_consumer_group(stream="", group="processors")

    @pytest.mark.asyncio
    async def test_create_consumer_group_empty_group_raises(self) -> None:
        """Test create_consumer_group with empty group."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Group name cannot be empty"):
            await stream.create_consumer_group(stream="telemetry", group="")


class TestRedisStreamConsume:
    """Tests for consume parameter validation."""

    @pytest.mark.asyncio
    async def test_consume_empty_stream_raises(self) -> None:
        """Test consume with empty stream raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Stream name cannot be empty"):
            # The validation happens when the async generator is created
            async for _ in stream.consume(
                stream="", group="group", consumer_name="consumer"
            ):
                pass

    @pytest.mark.asyncio
    async def test_consume_empty_group_raises(self) -> None:
        """Test consume with empty group raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Group name cannot be empty"):
            async for _ in stream.consume(
                stream="stream", group="", consumer_name="consumer"
            ):
                pass

    @pytest.mark.asyncio
    async def test_consume_empty_consumer_raises(self) -> None:
        """Test consume with empty consumer name raises ValueError."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Consumer name cannot be empty"):
            async for _ in stream.consume(
                stream="stream", group="group", consumer_name=""
            ):
                pass


class TestRedisStreamAcknowledge:
    """Tests for message acknowledgment."""

    @pytest.mark.asyncio
    async def test_acknowledge_success(self) -> None:
        """Test successful message acknowledgment."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xack = AsyncMock(return_value=1)

        await stream.acknowledge(
            stream="telemetry",
            group="processors",
            message_id="1234567890-0",
        )

        stream._client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_acknowledge_empty_stream_raises(self) -> None:
        """Test acknowledge with empty stream."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Stream name cannot be empty"):
            await stream.acknowledge(stream="", group="processors", message_id="123")

    @pytest.mark.asyncio
    async def test_acknowledge_empty_group_raises(self) -> None:
        """Test acknowledge with empty group."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Group name cannot be empty"):
            await stream.acknowledge(stream="telemetry", group="", message_id="123")

    @pytest.mark.asyncio
    async def test_acknowledge_empty_message_id_raises(self) -> None:
        """Test acknowledge with empty message_id."""
        stream = RedisStream(url="redis://localhost:6379/0")

        with pytest.raises(ValueError, match="Message ID cannot be empty"):
            await stream.acknowledge(
                stream="telemetry", group="processors", message_id=""
            )

    @pytest.mark.asyncio
    async def test_acknowledge_redis_error_raises(self) -> None:
        """Test acknowledge with Redis error."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xack = AsyncMock(side_effect=Exception("Redis error"))

        with pytest.raises(StreamError, match="Failed to acknowledge"):
            await stream.acknowledge(
                stream="telemetry", group="processors", message_id="123"
            )


class TestRedisStreamPublishWithTypes:
    """Tests for publish with type conversions."""

    @pytest.mark.asyncio
    async def test_publish_with_numeric_values(self) -> None:
        """Test publish converts numeric values to strings."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xadd = AsyncMock(return_value="1234567890-0")

        result = await stream.publish(
            stream="metrics", data={"value": 42, "ratio": 3.14}
        )

        assert result == "1234567890-0"
        stream._client.xadd.assert_called_once()
        # Verify all values were converted to strings
        call_args = stream._client.xadd.call_args
        data_arg = call_args[0][1]
        assert data_arg["value"] == "42"
        assert data_arg["ratio"] == "3.14"


class TestRedisStreamCreateGroupWithExisting:
    """Tests for consumer group creation with existing groups."""

    @pytest.mark.asyncio
    async def test_create_consumer_group_already_exists(self) -> None:
        """Test create_consumer_group when group already exists."""
        import redis.asyncio

        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        # Simulate BUSYGROUP error (group already exists)
        error = redis.asyncio.ResponseError(
            "BUSYGROUP Consumer Group name already exists"
        )
        stream._client.xgroup_create = AsyncMock(side_effect=error)

        # Should not raise - idempotent behavior
        await stream.create_consumer_group(stream="telemetry", group="processors")

        stream._client.xgroup_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_consumer_group_other_redis_error(self) -> None:
        """Test create_consumer_group with other Redis errors."""
        import redis.asyncio

        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        # Simulate other Redis error
        error = redis.asyncio.ResponseError("ERR Unknown error")
        stream._client.xgroup_create = AsyncMock(side_effect=error)

        with pytest.raises(StreamError, match="Failed to create consumer group"):
            await stream.create_consumer_group(stream="telemetry", group="processors")

    @pytest.mark.asyncio
    async def test_create_consumer_group_generic_error(self) -> None:
        """Test create_consumer_group with generic exception."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        error_msg = "Connection failed"
        stream._client.xgroup_create = AsyncMock(side_effect=Exception(error_msg))

        with pytest.raises(StreamError, match="Failed to create consumer group"):
            await stream.create_consumer_group(stream="telemetry", group="processors")


class TestRedisStreamConsumeWithMocks:
    """Tests for consume with mocked Redis responses."""

    @pytest.mark.asyncio
    async def test_consume_returns_messages(self) -> None:
        """Test consume successfully yields messages."""

        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()

        # Mock xreadgroup to return one message
        mock_result = [
            (
                "telemetry",
                [
                    (
                        "1234567890-0",
                        {"device_id": "device-01", "value": "95.5"},
                    )
                ],
            )
        ]
        stream._client.xreadgroup = AsyncMock(side_effect=[mock_result, None])

        consumed_messages = []
        async for msg_id, data in stream.consume(
            stream="telemetry", group="processors", consumer_name="worker-01"
        ):
            consumed_messages.append((msg_id, data))
            # Break after first message to avoid infinite loop
            break

        assert len(consumed_messages) == 1
        assert consumed_messages[0][0] == "1234567890-0"
        assert consumed_messages[0][1]["device_id"] == "device-01"

    @pytest.mark.asyncio
    async def test_consume_empty_result_continues(self) -> None:
        """Test consume continues when xreadgroup returns empty result."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()

        # Return None twice, then a result
        mock_result = [("telemetry", [("1234567890-0", {"device_id": "device-01"})])]
        stream._client.xreadgroup = AsyncMock(
            side_effect=[None, None, mock_result, None]
        )

        consumed_messages = []
        call_count = 0
        async for msg_id, data in stream.consume(
            stream="telemetry", group="processors", consumer_name="worker-01"
        ):
            consumed_messages.append((msg_id, data))
            call_count += 1
            if call_count >= 1:
                break

        assert len(consumed_messages) == 1
        # Verify xreadgroup was called multiple times (retrying on empty)
        assert stream._client.xreadgroup.call_count >= 3

    @pytest.mark.asyncio
    async def test_consume_with_nogroup_error(self) -> None:
        """Test consume raises ConsumerGroupError when group doesn't exist."""
        import redis.asyncio

        from src.streams.exceptions import ConsumerGroupError

        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        # Simulate NOGROUP error
        error = redis.asyncio.ResponseError("NOGROUP No such consumer group")
        stream._client.xreadgroup = AsyncMock(side_effect=error)

        with pytest.raises(ConsumerGroupError, match="Consumer group does not exist"):
            async for _ in stream.consume(
                stream="telemetry", group="processors", consumer_name="worker-01"
            ):
                pass

    @pytest.mark.asyncio
    async def test_consume_with_redis_error(self) -> None:
        """Test consume raises StreamError with other Redis errors."""
        import redis.asyncio

        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        # Simulate other Redis error
        error = redis.asyncio.ResponseError("ERR Some redis error")
        stream._client.xreadgroup = AsyncMock(side_effect=error)

        with pytest.raises(StreamError, match="Redis error during consumption"):
            async for _ in stream.consume(
                stream="telemetry", group="processors", consumer_name="worker-01"
            ):
                pass

    @pytest.mark.asyncio
    async def test_consume_with_generic_error(self) -> None:
        """Test consume raises StreamError with generic exceptions."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xreadgroup = AsyncMock(side_effect=Exception("Connection lost"))

        with pytest.raises(StreamError, match="Failed to consume from stream"):
            async for _ in stream.consume(
                stream="telemetry", group="processors", consumer_name="worker-01"
            ):
                pass


class TestRedisStreamClose:
    """Tests for connection closing."""

    @pytest.mark.asyncio
    async def test_close_success(self) -> None:
        """Test successful connection closure."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.close = AsyncMock()

        await stream.close()

        stream._client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_suppresses_exceptions(self) -> None:
        """Test close suppresses exceptions gracefully."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.close = AsyncMock(side_effect=Exception("Already closed"))

        # Should not raise
        await stream.close()


__all__ = [
    "TestRedisStreamInitialization",
    "TestRedisStreamPublish",
    "TestRedisStreamCreateConsumerGroup",
    "TestRedisStreamConsume",
    "TestRedisStreamAcknowledge",
    "TestRedisStreamPublishWithTypes",
    "TestRedisStreamCreateGroupWithExisting",
    "TestRedisStreamConsumeWithMocks",
    "TestRedisStreamClose",
]
