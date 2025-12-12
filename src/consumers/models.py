"""Consumer-specific data models.

This module defines models used within the consumer library for message
processing and internal state management.

Classes:
    ConsumerMessage: Wrapper for consumed stream messages
    ConsumerState: Internal consumer state tracking
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, kw_only=True, slots=True)
class ConsumerMessage:
    """Wrapper for consumed stream messages.

    Provides a standardized interface for messages consumed from various
    streaming platforms.

    Attributes:
        message_id: Unique identifier for the message
        stream_name: Name of the source stream
        data: Raw message data (not yet deserialized)
        timestamp: When message was consumed
        retry_count: Number of times this message has been retried

    Example:
        message = ConsumerMessage(
            message_id="1234567890-0",
            stream_name="telemetry",
            data={"device": "router-01", "value": 85.5},
            timestamp=datetime.now(UTC),
            retry_count=0
        )
    """
    message_id: str
    stream_name: str
    data: dict[str, Any]
    timestamp: datetime
    retry_count: int = 0


@dataclass(frozen=True, kw_only=True, slots=True)
class ConsumerState:
    """Consumer state tracking information.

    Tracks internal consumer state for monitoring and debugging.

    Attributes:
        consumer_name: Unique name of this consumer
        group_name: Consumer group this consumer belongs to
        messages_processed: Total messages successfully processed
        messages_failed: Total messages that failed processing
        last_message_id: ID of last successfully processed message
        is_running: Whether consumer is currently active

    Example:
        state = ConsumerState(
            consumer_name="worker-01",
            group_name="telemetry-processors",
            messages_processed=1000,
            messages_failed=5,
            last_message_id="1234567890-0",
            is_running=True
        )
    """
    consumer_name: str
    group_name: str
    messages_processed: int
    messages_failed: int
    last_message_id: str | None
    is_running: bool


__all__ = ["ConsumerMessage", "ConsumerState"]
