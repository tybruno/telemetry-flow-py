"""Stream consumer for telemetry events.

Class:
    TelemetryConsumer: Consumes events from telemetry stream.
"""
import logging
from collections.abc import AsyncIterator

from src.core.models import TelemetryEvent
from src.core.protocols import StreamProtocol

_log = logging.getLogger(__name__)


class TelemetryConsumer:
    """Consumes telemetry events from stream with consumer groups.
    
    Attributes:
        _stream: Stream protocol implementation.
        _group_name: Consumer group name.
        _consumer_name: This consumer's unique name.
    """
    __slots__ = ("_stream", "_group_name", "_consumer_name")
    
    _stream: StreamProtocol
    _group_name: str
    _consumer_name: str
    
    def __init__(
        self,
        *,
        stream: StreamProtocol,
        group_name: str,
        consumer_name: str,
    ) -> None:
        """Initialize consumer."""
        raise NotImplementedError
    
    async def consume_events(self) -> AsyncIterator[TelemetryEvent]:
        """Consume telemetry events from stream.
        
        Yields:
            TelemetryEvent instances from the stream.
        """
        raise NotImplementedError
        yield  # Make this a generator


__all__ = ["TelemetryConsumer"]
