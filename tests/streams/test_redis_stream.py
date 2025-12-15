"""Tests for Redis Streams implementation."""

from unittest.mock import AsyncMock

import pytest
import redis

from src.streams.exceptions import StreamError
from src.streams.redis_stream import RedisStream


class TestRedisStreamPublish:
    """Tests for publish functionality."""

    @pytest.mark.asyncio
    async def test_publish_success(self) -> None:
        """Test successful event publishing."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xadd = AsyncMock(return_value="1234567890-0")

        message_id = await stream.publish(
            stream="telemetry", data={"device_id": "router-01", "value": 85.5}
        )

        assert message_id == "1234567890-0"

    @pytest.mark.asyncio
    async def test_publish_error_raises(self) -> None:
        """Test publish error handling."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xadd = AsyncMock(side_effect=Exception("Redis error"))

        with pytest.raises(StreamError):
            await stream.publish(stream="telemetry", data={"key": "value"})


class TestRedisStreamConsume:
    """Tests for consume functionality."""

    @pytest.mark.asyncio
    async def test_consume_yields_messages(self) -> None:
        """Test consuming messages from stream."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()

        stream._client.xreadgroup = AsyncMock(
            side_effect=[
                [[b"telemetry", [(b"1-0", {b"device_id": b"router-01"})]]],
                None,
            ]
        )

        messages = []
        async for msg_id, data in stream.consume(
            stream="telemetry", group="processors", consumer_name="worker-01"
        ):
            messages.append((msg_id, data))
            break

        assert len(messages) == 1
        # message_id will be bytes from Redis
        assert messages[0][0] == b"1-0"


class TestRedisStreamAcknowledge:
    """Tests for acknowledge functionality."""

    @pytest.mark.asyncio
    async def test_acknowledge_success(self) -> None:
        """Test successful message acknowledgment."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xack = AsyncMock(return_value=1)

        await stream.acknowledge(
            stream="telemetry", group="processors", message_id="1234567890-0"
        )

        stream._client.xack.assert_called_once()


class TestRedisStreamConsumerGroup:
    """Tests for consumer group management."""

    @pytest.mark.asyncio
    async def test_create_consumer_group_success(self) -> None:
        """Test successful consumer group creation."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        stream._client.xgroup_create = AsyncMock()

        await stream.create_consumer_group(
            stream="telemetry", group="processors", start_id="$"
        )

        stream._client.xgroup_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_consumer_group_already_exists_ignores(self) -> None:
        """Test consumer group creation when group exists."""
        stream = RedisStream(url="redis://localhost:6379/0")
        stream._client = AsyncMock()
        error = redis.ResponseError("BUSYGROUP Consumer Group name already exists")
        stream._client.xgroup_create = AsyncMock(side_effect=error)

        # Should not raise
        await stream.create_consumer_group(
            stream="telemetry", group="processors", start_id="$"
        )
