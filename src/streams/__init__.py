"""Stream infrastructure for event streaming and backpressure.

Implementations:
    RedisStream: Redis Streams implementation

Models:
    StreamMessage: Stream message model

Exceptions:
    StreamError: Base exception for stream errors
    ConsumerGroupError: Consumer group operation failures
    BackpressureError: Backpressure handling errors
"""

from src.streams.exceptions import (
    BackpressureError,
    ConsumerGroupError,
    StreamError,
)
from src.streams.models import StreamMessage
from src.streams.redis_stream import RedisStream

__all__ = [
    "BackpressureError",
    "ConsumerGroupError",
    "RedisStream",
    "StreamError",
    "StreamMessage",
]
