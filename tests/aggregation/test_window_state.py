"""Tests for window state management functionality.

Tests window state tracking, boundary calculations, and state transitions.
"""

from datetime import datetime, timezone

from src.utils.time_windows import calculate_window_bounds


class TestWindowState:
    """Tests for window state management."""

    def test_create_window_state(self) -> None:
        """Test creating new window state.

        Verifies window state initialized with correct boundaries.
        """
        timestamp = datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)
        start, end = calculate_window_bounds(timestamp, window_size=60)

        assert start == datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)
        assert end == datetime(2025, 12, 12, 10, 31, 0, tzinfo=timezone.utc)

    def test_calculate_window_boundaries(self) -> None:
        """Test window boundary calculation.

        Verifies start/end timestamps calculated correctly based on
        window size and alignment.
        """
        timestamp = datetime(2025, 12, 12, 10, 30, 45, tzinfo=timezone.utc)
        start, end = calculate_window_bounds(timestamp, window_size=60)

        # Should align to minute boundary
        assert start.second == 0
        assert (end - start).total_seconds() == 60

    def test_event_belongs_to_window(self) -> None:
        """Test determining if event belongs to window.

        Verifies timestamp comparison logic for window membership.
        """
        window_start = datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)
        window_end = datetime(2025, 12, 12, 10, 31, 0, tzinfo=timezone.utc)

        event_ts = datetime(2025, 12, 12, 10, 30, 30, tzinfo=timezone.utc)

        belongs_to_window = window_start <= event_ts < window_end
        assert belongs_to_window is True

    def test_transition_to_next_window(self) -> None:
        """Test transitioning to next window.

        Verifies new window created with correct boundaries when
        current window completes.
        """
        ts1 = datetime(2025, 12, 12, 10, 30, 30, tzinfo=timezone.utc)
        start1, end1 = calculate_window_bounds(ts1, window_size=60)

        ts2 = datetime(2025, 12, 12, 10, 31, 30, tzinfo=timezone.utc)
        start2, end2 = calculate_window_bounds(ts2, window_size=60)

        # Second window should start where first ended
        assert start2 == end1
