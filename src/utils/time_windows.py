"""Time window calculation utilities.

This module provides utilities for calculating time window boundaries
used in aggregation and windowing operations.

Classes:
    None.

Functions:
    calculate_window_bounds: Calculate window start/end timestamps.

Example:
    Calculating window boundaries for aggregation::

        from utils import calculate_window_bounds
        from datetime import datetime, timezone

        # 60-second window
        timestamp = datetime(2025, 12, 12, 10, 30, 45, tzinfo=timezone.utc)
        start, end = calculate_window_bounds(
            timestamp=timestamp,
            window_size=60
        )
        # start: 2025-12-12 10:30:00
        # end:   2025-12-12 10:31:00
"""

import logging as _log
from datetime import datetime, timedelta


def calculate_window_bounds(
    timestamp: datetime,
    window_size: int,
) -> tuple[datetime, datetime]:
    """Calculate aligned window start and end times for a timestamp.

    Aligns the timestamp to window boundaries based on the window size,
    returning the window start and end times. Used for consistent
    windowing across distributed aggregators.

    Args:
        timestamp: Event timestamp to calculate window for.
        window_size: Window size in seconds. Must be positive.

    Returns:
        Tuple of (window_start, window_end) as datetime objects.
        window_start is aligned to window boundary.
        window_end = window_start + window_size seconds.

    Raises:
        ValueError: If window_size is not positive or timestamp is None.

    Example:
        60-second tumbling window::

            from datetime import datetime, timezone

            ts = datetime(2025, 12, 12, 10, 30, 45, tzinfo=timezone.utc)
            start, end = calculate_window_bounds(ts, window_size=60)

            # start: 2025-12-12T10:30:00Z (aligned to minute)
            # end:   2025-12-12T10:31:00Z (start + 60 seconds)
    """
    if not timestamp:
        error_message = "timestamp cannot be None"
        _log.error(error_message)
        raise ValueError(error_message) from None

    if window_size <= 0:
        error_message = "window_size must be positive: %d"
        _log.error(error_message, window_size)
        raise ValueError(error_message % window_size) from None

    # Get timestamp as seconds since epoch
    epoch_seconds = timestamp.timestamp()

    # Align to window boundary
    aligned_seconds = (epoch_seconds // window_size) * window_size

    # Create window start and end
    window_start = datetime.fromtimestamp(aligned_seconds, tz=timestamp.tzinfo)
    window_end = window_start + timedelta(seconds=window_size)

    bounds = (window_start, window_end)
    return bounds


__all__ = ["calculate_window_bounds"]
