"""Redis Streams implementation.

This module provides a Redis Streams-based implementation of the
StreamProtocol for event publishing and consumption.

Classes:
    RedisStream: Redis Streams implementation of StreamProtocol.

Example:
    Basic Redis Streams usage::

        from streams import RedisStream

        stream = RedisStream(url="redis://localhost:6379")

        # Publish event
        msg_id = await stream.publish(
            stream="telemetry",
            data={"device_id": "router-01", "value": 85.5}
        )

        # Create consumer group
        await stream.create_consumer_group(
            stream="telemetry",
            group="processors",
            start_id="$"
        )

        # Consume events
        async for msg_id, data in stream.consume(
            stream="telemetry",
            group="processors",
            consumer_name="worker-01"
        ):
            await process(data)
            await stream.acknowledge(
                stream="telemetry",
                group="processors",
                message_id=msg_id
            )
"""

import logging as _log
from collections.abc import AsyncGenerator
from contextlib import suppress
from typing import Any

import redis.asyncio as redis

from src.streams.exceptions import ConsumerGroupError, StreamError


class RedisStream:
    """Redis Streams implementation of StreamProtocol.

    Implements stream publishing and consumption using Redis Streams
    with consumer groups for distributed processing and at-least-once
    delivery guarantees.

    Attributes:
        _url: Redis connection URL.
        _client: Redis async client instance.

    Example:
        Complete stream workflow::

            stream = RedisStream(url="redis://localhost:6379/0")

            # Setup
            await stream.create_consumer_group(
                stream="events",
                group="workers",
                start_id="$"
            )

            # Publish
            msg_id = await stream.publish(
                stream="events",
                data={"type": "telemetry", "value": 95.5}
            )

            # Consume
            async for msg_id, data in stream.consume(
                stream="events",
                group="workers",
                consumer_name="worker-01"
            ):
                await process_event(data)
                await stream.acknowledge(
                    stream="events",
                    group="workers",
                    message_id=msg_id
                )
    """

    __slots__ = ("_client", "_url")

    _url: str
    _client: redis.Redis  # type: ignore[type-arg]

    def __init__(self, *, url: str) -> None:
        """Initialize Redis stream connection.

        Args:
            url: Redis connection URL (e.g., "redis://localhost:6379/0").

        Raises:
            ValueError: If URL is invalid or empty.
            ConnectionError: If Redis connection cannot be established.
        """
        if not url or not url.strip():
            error_message = "Redis URL cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        self._url = url
        self._client = redis.from_url(url, decode_responses=True)
        _log.info("Redis stream initialized: url=%s", url)

    async def publish(self, stream: str, data: dict[str, Any]) -> str:
        """Publish data to Redis stream using XADD.

        Args:
            stream: Stream name.
            data: Data dictionary to publish.

        Returns:
            Message ID assigned by Redis (e.g., "1234567890-0").

        Raises:
            ValueError: If stream name is empty or data is invalid.
            StreamError: If publish operation fails.
        """
        if not stream or not stream.strip():
            error_message = "Stream name cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        if not data:
            error_message = "Data cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        try:
            # Convert all values to strings for Redis
            string_data = {k: str(v) for k, v in data.items()}
            message_id: str = await self._client.xadd(stream, string_data)
            _log.debug("Published to stream: stream=%s, msg_id=%s", stream, message_id)
            return message_id
        except Exception as e:
            error_message = "Failed to publish to stream: %s"
            _log.error(error_message, str(e))
            raise StreamError(error_message % str(e)) from e

    async def consume(
        self,
        stream: str,
        group: str,
        consumer_name: str,
    ) -> AsyncGenerator[tuple[str, dict[str, Any]], None]:
        """Consume from Redis stream with consumer group using XREADGROUP.

        Args:
            stream: Stream name.
            group: Consumer group name.
            consumer_name: Unique consumer instance name.

        Yields:
            Tuples of (message_id, data) for each consumed message.

        Raises:
            ValueError: If stream, group, or consumer_name is empty.
            ConsumerGroupError: If consumer group doesn't exist.
            StreamError: If consumption fails.
        """
        if not stream or not stream.strip():
            error_message = "Stream name cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        if not group or not group.strip():
            error_message = "Group name cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        if not consumer_name or not consumer_name.strip():
            error_message = "Consumer name cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        _log.info(
            "Starting consumption: stream=%s, group=%s, consumer=%s",
            stream,
            group,
            consumer_name,
        )

        while True:
            try:
                # Read from consumer group, blocking for 1 second
                result = await self._client.xreadgroup(
                    groupname=group,
                    consumername=consumer_name,
                    streams={stream: ">"},
                    count=10,
                    block=1000,
                )

                if not result:
                    continue

                # Result format: [(stream_name, [(msg_id, data), ...])]
                for _, messages in result:
                    for message_id, data in messages:
                        _log.debug(
                            "Consumed message: stream=%s, msg_id=%s", stream, message_id
                        )
                        yield message_id, data

            except redis.ResponseError as e:
                if "NOGROUP" in str(e):
                    error_message = "Consumer group does not exist: %s"
                    _log.error(error_message, group)
                    raise ConsumerGroupError(error_message % group) from e
                error_message = "Redis error during consumption: %s"
                _log.error(error_message, str(e))
                raise StreamError(error_message % str(e)) from e
            except Exception as e:
                error_message = "Failed to consume from stream: %s"
                _log.error(error_message, str(e))
                raise StreamError(error_message % str(e)) from e

    async def acknowledge(
        self,
        stream: str,
        group: str,
        message_id: str,
    ) -> None:
        """Acknowledge message processing with XACK.

        Removes message from pending list, marking it as successfully
        processed for at-least-once delivery.

        Args:
            stream: Stream name.
            group: Consumer group name.
            message_id: Message ID to acknowledge.

        Raises:
            ValueError: If any parameter is empty.
            StreamError: If acknowledgment fails.
        """
        if not stream or not stream.strip():
            error_message = "Stream name cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        if not group or not group.strip():
            error_message = "Group name cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        if not message_id or not message_id.strip():
            error_message = "Message ID cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        try:
            await self._client.xack(stream, group, message_id)  # type: ignore[no-untyped-call]
            _log.debug("Acknowledged message: stream=%s, msg_id=%s", stream, message_id)
        except Exception as e:
            error_message = "Failed to acknowledge message: %s"
            _log.error(error_message, str(e))
            raise StreamError(error_message % str(e)) from e

    async def create_consumer_group(
        self,
        stream: str,
        group: str,
        start_id: str = "$",
    ) -> None:
        """Create consumer group with XGROUP CREATE.

        Creates a consumer group for distributed stream processing.
        Idempotent - succeeds if group already exists.

        Args:
            stream: Stream name.
            group: Consumer group name to create.
            start_id: Starting position ("$" for new messages,
                "0" for all messages).

        Raises:
            ValueError: If stream or group name is empty.
            StreamError: If group creation fails.
        """
        if not stream or not stream.strip():
            error_message = "Stream name cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        if not group or not group.strip():
            error_message = "Group name cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        try:
            await self._client.xgroup_create(
                name=stream,
                groupname=group,
                id=start_id,
                mkstream=True,
            )
            _log.info("Created consumer group: stream=%s, group=%s", stream, group)
        except redis.ResponseError as e:
            # Ignore if group already exists
            if "BUSYGROUP" in str(e):
                _log.debug(
                    "Consumer group already exists: stream=%s, group=%s", stream, group
                )
                return
            error_message = "Failed to create consumer group: %s"
            _log.error(error_message, str(e))
            raise StreamError(error_message % str(e)) from e
        except Exception as e:
            error_message = "Failed to create consumer group: %s"
            _log.error(error_message, str(e))
            raise StreamError(error_message % str(e)) from e

    async def close(self) -> None:
        """Close Redis connection."""
        with suppress(Exception):
            await self._client.close()
            _log.info("Redis connection closed")


__all__ = ["RedisStream"]
