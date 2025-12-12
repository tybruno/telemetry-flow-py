"""Stream infrastructure models.

Classes:
    StreamMessage: Wrapper for stream messages.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True, kw_only=True)
class StreamMessage:
    """Redis stream message wrapper.

    Attributes:
        stream_id: Unique message ID from stream.
        data: Message payload data.
        timestamp_ms: Message timestamp in milliseconds.
    """

    stream_id: str
    data: dict[str, Any]
    timestamp_ms: int


__all__ = ["StreamMessage"]
