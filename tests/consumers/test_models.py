"""Tests for consumer models."""

from datetime import datetime, timezone

import pytest

from src.consumers.models import ConsumerMessage, ConsumerState


class TestConsumerMessage:
    """Test suite for ConsumerMessage model."""

    def test_consumer_message_creation(self) -> None:
        """Test ConsumerMessage can be created with all fields."""
        timestamp = datetime(2025, 12, 15, 10, 0, 0, tzinfo=timezone.utc)
        
        message = ConsumerMessage(
            message_id="1234567890-0",
            stream_name="telemetry",
            data={"device": "router-01", "value": 85.5},
            timestamp=timestamp,
            retry_count=0,
        )

        assert message.message_id == "1234567890-0"
        assert message.stream_name == "telemetry"
        assert message.data == {"device": "router-01", "value": 85.5}
        assert message.timestamp == timestamp
        assert message.retry_count == 0

    def test_consumer_message_default_retry_count(self) -> None:
        """Test ConsumerMessage has default retry_count of 0."""
        message = ConsumerMessage(
            message_id="1234567890-0",
            stream_name="telemetry",
            data={},
            timestamp=datetime.now(timezone.utc),
        )

        assert message.retry_count == 0

    def test_consumer_message_is_frozen(self) -> None:
        """Test ConsumerMessage is immutable."""
        message = ConsumerMessage(
            message_id="1234567890-0",
            stream_name="telemetry",
            data={},
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(AttributeError):
            message.retry_count = 5  # type: ignore[misc]


class TestConsumerState:
    """Test suite for ConsumerState model."""

    def test_consumer_state_creation(self) -> None:
        """Test ConsumerState can be created with all fields."""
        state = ConsumerState(
            consumer_name="worker-01",
            group_name="telemetry-processors",
            messages_processed=1000,
            messages_failed=5,
            last_message_id="1234567890-0",
            is_running=True,
        )

        assert state.consumer_name == "worker-01"
        assert state.group_name == "telemetry-processors"
        assert state.messages_processed == 1000
        assert state.messages_failed == 5
        assert state.last_message_id == "1234567890-0"
        assert state.is_running is True

    def test_consumer_state_with_none_last_message(self) -> None:
        """Test ConsumerState allows None for last_message_id."""
        state = ConsumerState(
            consumer_name="worker-01",
            group_name="telemetry-processors",
            messages_processed=0,
            messages_failed=0,
            last_message_id=None,
            is_running=False,
        )

        assert state.last_message_id is None

    def test_consumer_state_is_frozen(self) -> None:
        """Test ConsumerState is immutable."""
        state = ConsumerState(
            consumer_name="worker-01",
            group_name="telemetry-processors",
            messages_processed=0,
            messages_failed=0,
            last_message_id=None,
            is_running=True,
        )

        with pytest.raises(AttributeError):
            state.is_running = False  # type: ignore[misc]


__all__: list[str] = []
