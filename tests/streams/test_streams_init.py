"""Tests for streams __init__ module."""

from src.streams import (
    BackpressureError,
    ConsumerGroupError,
    RedisStream,
    StreamError,
    StreamMessage,
)


class TestStreamsInit:
    """Test suite for streams __init__ module."""

    def test_redis_stream_is_importable(self) -> None:
        """Test RedisStream can be imported."""
        assert RedisStream is not None

    def test_stream_message_is_importable(self) -> None:
        """Test StreamMessage can be imported."""
        assert StreamMessage is not None

    def test_stream_error_is_importable(self) -> None:
        """Test StreamError can be imported."""
        assert StreamError is not None

    def test_consumer_group_error_is_importable(self) -> None:
        """Test ConsumerGroupError can be imported."""
        assert ConsumerGroupError is not None

    def test_backpressure_error_is_importable(self) -> None:
        """Test BackpressureError can be imported."""
        assert BackpressureError is not None


__all__: list[str] = []
