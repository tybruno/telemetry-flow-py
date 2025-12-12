"""Time window utilities.

Functions:
    calculate_window_bounds: Calculate window start/end times.
"""

from datetime import datetime, timedelta


def calculate_window_bounds(
    timestamp: datetime,
    window_size: int,
) -> tuple[datetime, datetime]:
    """Calculate window bounds for a timestamp.

    Args:
        timestamp: Timestamp to calculate window for.
        window_size: Window size in seconds.

    Returns:
        Tuple of (window_start, window_end).
    """
    raise NotImplementedError


__all__ = ["calculate_window_bounds"]
