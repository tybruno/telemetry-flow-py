"""Time-window aggregation for telemetry metrics.

Class:
    TumblingWindowAggregator: Tumbling window aggregation.
"""
import logging
from datetime import timedelta

from src.core.models import TelemetryEvent
from src.processor.models import AggregatedMetric

_log = logging.getLogger(__name__)


class TumblingWindowAggregator:
    """Tumbling window aggregator for telemetry metrics.
    
    Aggregates metrics over fixed-size time windows without overlap.
    
    Attributes:
        _window_size: Window duration in seconds.
    """
    __slots__ = ("_window_size", "_window_delta")
    
    _window_size: int
    _window_delta: timedelta
    
    def __init__(self, *, window_size: int) -> None:
        """Initialize aggregator with window size."""
        raise NotImplementedError
    
    async def aggregate(self, event: TelemetryEvent) -> AggregatedMetric | None:
        """Aggregate event into time window.
        
        Args:
            event: Telemetry event to aggregate.
        
        Returns:
            AggregatedMetric if window completed, None if still accumulating.
        """
        raise NotImplementedError


__all__ = ["TumblingWindowAggregator"]
