"""Protocol definitions for infrastructure interfaces.

This module defines the contracts (protocols) that all infrastructure
implementations must satisfy. Using Python protocols enables structural
typing and loose coupling between services and infrastructure.

Protocols:
    StreamProtocol: Interface for stream publishing and consumption.
    StorageProtocol: Interface for state persistence operations.
    AlerterProtocol: Interface for sending anomaly alerts.

Example:
    Implementing a custom stream backend::

        class KafkaStream:
            async def publish(self, stream: str, data: dict) -> str:
                # Custom Kafka implementation
                return message_id

            async def consume(
                self,
                stream: str,
                group: str
            ) -> AsyncIterator[dict]:
                # Custom Kafka implementation
                yield message

        # KafkaStream satisfies StreamProtocol without inheritance
"""

from collections.abc import AsyncIterator
from typing import Any, Protocol


class StreamProtocol(Protocol):
    """Protocol for stream publishing and consumption operations.

    Defines the contract that all stream implementations must satisfy.
    Implementations can be Redis Streams, Kafka, RabbitMQ, etc.

    Example:
        Using a stream in a service::

            class IngestService:
                def __init__(self, stream: StreamProtocol):
                    self._stream = stream

                async def ingest(self, data: dict) -> str:
                    event_id = await self._stream.publish("telemetry", data)
                    return event_id
    """

    async def publish(self, stream: str, data: dict[str, Any]) -> str:
        """Publish data to a stream.

        Args:
            stream: Name of the stream to publish to.
            data: Dictionary containing the event data to publish.

        Returns:
            Unique identifier for the published message.

        Raises:
            StreamError: If publication fails.

        Example:
            Publishing an event::

                message_id = await stream.publish(
                    stream="telemetry",
                    data={"device_id": "router-01", "value": 95.5}
                )
        """
        ...

    async def consume(
        self,
        stream: str,
        group: str,
        consumer_name: str,
    ) -> AsyncIterator[tuple[str, dict[str, Any]]]:
        """Consume messages from a stream using consumer groups.

        Args:
            stream: Name of the stream to consume from.
            group: Consumer group name for distributed processing.
            consumer_name: Unique name for this consumer instance.

        Yields:
            Tuples of (message_id, data) for each consumed message.

        Raises:
            StreamError: If consumption fails.

        Example:
            Consuming events::

                async for msg_id, data in stream.consume(
                    stream="telemetry",
                    group="processors",
                    consumer_name="worker-01"
                ):
                    await process_event(data)
                    await stream.acknowledge(
                        stream="telemetry",
                        group="processors",
                        message_id=msg_id
                    )
        """
        ...

    async def acknowledge(
        self,
        stream: str,
        group: str,
        message_id: str,
    ) -> None:
        """Acknowledge successful processing of a message.

        Removes message from pending list for at-least-once delivery.

        Args:
            stream: Name of the stream.
            group: Consumer group that received the message.
            message_id: ID of the message to acknowledge.

        Raises:
            StreamError: If acknowledgment fails.

        Example:
            Acknowledging after processing::

                async for msg_id, data in stream.consume(...):
                    try:
                        await process(data)
                        await stream.acknowledge(
                            stream="telemetry",
                            group="processors",
                            message_id=msg_id
                        )
                    except Exception:
                        # Message stays in pending for retry
                        _log.error("Processing failed for %s", msg_id)
        """
        ...

    async def create_consumer_group(
        self,
        stream: str,
        group: str,
        start_id: str = "$",
    ) -> None:
        """Create a consumer group for distributed processing.

        Must be called before consumers can join the group.

        Args:
            stream: Name of the stream.
            group: Name for the consumer group.
            start_id: Starting position ("$" for new, "0" for all).

        Raises:
            StreamError: If group creation fails.

        Example:
            Creating consumer group::

                await stream.create_consumer_group(
                    stream="telemetry",
                    group="processors",
                    start_id="$"
                )
        """
        ...


class StorageProtocol(Protocol):
    """Protocol for state persistence and retrieval operations.

    Defines the contract for storing and retrieving worker state,
    aggregation windows, and coordination data.

    Example:
        Using storage in a processor::

            class Aggregator:
                def __init__(self, storage: StorageProtocol):
                    self._storage = storage

                async def save_window(self, key: str, state: dict) -> None:
                    await self._storage.set(key, state)
    """

    async def set(
        self,
        key: str,
        value: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Store a value with optional TTL.

        Args:
            key: Storage key for the value.
            value: Dictionary value to store.
            ttl: Optional time-to-live in seconds.

        Raises:
            StorageError: If storage operation fails.

        Example:
            Storing window state::

                await storage.set(
                    key="window:device-01:cpu",
                    value={"sum": 450.5, "count": 5},
                    ttl=3600
                )
        """
        ...

    async def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve a value by key.

        Args:
            key: Storage key to retrieve.

        Returns:
            Dictionary value if key exists, None otherwise.

        Raises:
            StorageError: If retrieval operation fails.

        Example:
            Retrieving window state::

                state = await storage.get("window:device-01:cpu")
                if state:
                    total = state["sum"]
        """
        ...

    async def delete(self, key: str) -> bool:
        """Delete a value by key.

        Args:
            key: Storage key to delete.

        Returns:
            True if key was deleted, False if key didn't exist.

        Raises:
            StorageError: If deletion operation fails.

        Example:
            Deleting expired state::

                deleted = await storage.delete("window:device-01:cpu")
        """
        ...


class AlerterProtocol(Protocol):
    """Protocol for sending anomaly alert notifications.

    Defines the contract for alert delivery systems. Implementations
    can send alerts to console, email, Slack, PagerDuty, etc.

    Example:
        Using an alerter in a detector::

            class AnomalyDetector:
                def __init__(self, alerter: AlerterProtocol):
                    self._alerter = alerter

                async def handle_anomaly(self, event: dict) -> None:
                    await self._alerter.send_alert(
                        severity="high",
                        message="CPU threshold exceeded",
                        context=event
                    )
    """

    async def send_alert(
        self,
        *,
        severity: str,
        message: str,
        context: dict[str, Any],
    ) -> None:
        """Send an anomaly alert.

        Args:
            severity: Alert severity level (low, medium, high, critical).
            message: Human-readable alert message.
            context: Additional context data for the alert.

        Raises:
            AlertError: If alert delivery fails.

        Example:
            Sending a critical alert::

                await alerter.send_alert(
                    severity="critical",
                    message="Device offline: router-01",
                    context={
                        "device_id": "router-01",
                        "last_seen": "2024-12-12T10:30:00Z"
                    }
                )
        """
        ...


__all__ = [
    "AlerterProtocol",
    "StorageProtocol",
    "StreamProtocol",
]
