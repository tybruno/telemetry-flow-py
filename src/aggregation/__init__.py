"""Reusable time-windowed aggregation library.

This library provides generic windowed aggregation capabilities for processing
time-series metric data. It is fully domain-agnostic and can aggregate any
numeric metrics with configurable window sizes and statistical calculations.

Classes:
    BaseAggregator: Abstract base with shared window utilities
    TumblingWindowAggregator: Tumbling window aggregator implementation
    WindowMetrics: Generic window statistics result
    WindowBounds: Window timestamp boundaries

Example:
    Basic aggregation setup::
    
        from aggregation import TumblingWindowAggregator, WindowMetrics
        
        aggregator = TumblingWindowAggregator(
            window_size_seconds=60,
            storage=storage_implementation
        )
        
        result = await aggregator.aggregate(event)
        if result:
            print(f"Window complete: avg={result.average}")
"""

__all__ = [
    "BaseAggregator",
    "TumblingWindowAggregator",
    "WindowMetrics",
    "WindowBounds",
]
