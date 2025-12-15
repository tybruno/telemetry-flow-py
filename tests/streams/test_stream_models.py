"""Tests for stream models."""

import pytest

from src.streams.models import StreamMessage


class TestStreamMessage:
    """Test suite for StreamMessage model."""

    def test_stream_message_creation(self) -> None:
        """Test StreamMessage can be created with all fields."""
        message = StreamMessage(
            stream_id="1234567890-0",
            data={"device": "router-01", "value": 85.5},
            timestamp_ms=1734252000000,
        )

        assert message.stream_id == "1234567890-0"
        assert message.data == {"device": "router-01", "value": 85.5}
        assert message.timestamp_ms == 1734252000000

    def test_stream_message_is_frozen(self) -> None:
        """Test StreamMessage is immutable."""
        message = StreamMessage(
            stream_id="1234567890-0",
            data={},
            timestamp_ms=1734252000000,
        )

        with pytest.raises(AttributeError):
            message.stream_id = "9876543210-0"  # type: ignore[misc]

    def test_stream_message_empty_data(self) -> None:
        """Test StreamMessage accepts empty data."""
        message = StreamMessage(
            stream_id="1234567890-0",
            data={},
            timestamp_ms=1734252000000,
        )

        assert message.data == {}


__all__: list[str] = []
