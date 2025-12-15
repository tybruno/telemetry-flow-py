"""Tests for time window utilities."""

from datetime import datetime, timezone

import pytest

from src.utils.time_windows import calculate_window_bounds


class TestCalculateWindowBounds:
    """Test suite for calculate_window_bounds function."""

    def test_calculate_window_bounds_aligns_to_boundary(self) -> None:
        """Test window boundaries align correctly."""
        timestamp = datetime(2025, 12, 12, 10, 30, 45, tzinfo=timezone.utc)
        start, end = calculate_window_bounds(timestamp, window_size=60)

        # Should align to minute boundary
        expected_start = datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)
        expected_end = datetime(2025, 12, 12, 10, 31, 0, tzinfo=timezone.utc)

        assert start == expected_start
        assert end == expected_end

    def test_calculate_window_bounds_exactly_on_boundary(self) -> None:
        """Test timestamp exactly on window boundary."""
        timestamp = datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)
        start, end = calculate_window_bounds(timestamp, window_size=60)

        expected_start = datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)
        expected_end = datetime(2025, 12, 12, 10, 31, 0, tzinfo=timezone.utc)

        assert start == expected_start
        assert end == expected_end

    @pytest.mark.parametrize(
        ("window_size", "expected_start_minute"),
        [
            (60, 32),  # 1 minute window - aligns to 10:32:00
            (300, 30),  # 5 minute window - aligns to 10:30:00
            (3600, 0),  # 1 hour window - aligns to 10:00:00
        ],
    )
    def test_calculate_window_bounds_different_sizes(
        self,
        window_size: int,
        expected_start_minute: int,
    ) -> None:
        """Test different window sizes align correctly.

        Args:
            window_size: Size of window in seconds.
            expected_start_minute: Expected minute of window start.
        """
        timestamp = datetime(2025, 12, 12, 10, 32, 45, tzinfo=timezone.utc)
        start, end = calculate_window_bounds(timestamp, window_size=window_size)

        assert start.minute == expected_start_minute
        duration_seconds = (end - start).total_seconds()
        assert duration_seconds == window_size

    def test_calculate_window_bounds_preserves_timezone(self) -> None:
        """Test timezone is preserved in returned bounds."""
        timestamp = datetime(2025, 12, 12, 10, 30, 45, tzinfo=timezone.utc)
        start, end = calculate_window_bounds(timestamp, window_size=60)

        assert start.tzinfo == timezone.utc
        assert end.tzinfo == timezone.utc

    def test_calculate_window_bounds_invalid_window_size_zero(self) -> None:
        """Test window_size of 0 raises ValueError."""
        timestamp = datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)

        with pytest.raises(ValueError, match="window_size must be positive"):
            calculate_window_bounds(timestamp, window_size=0)

    def test_calculate_window_bounds_invalid_window_size_negative(self) -> None:
        """Test negative window_size raises ValueError."""
        timestamp = datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)

        with pytest.raises(ValueError, match="window_size must be positive"):
            calculate_window_bounds(timestamp, window_size=-60)

    def test_calculate_window_bounds_none_timestamp_raises(self) -> None:
        """Test None timestamp raises ValueError."""
        with pytest.raises(ValueError, match="timestamp cannot be None"):
            calculate_window_bounds(None, window_size=60)  # type: ignore[arg-type]

    def test_calculate_window_bounds_large_window(self) -> None:
        """Test calculation with large window size."""
        timestamp = datetime(2025, 12, 12, 14, 32, 45, tzinfo=timezone.utc)
        start, end = calculate_window_bounds(timestamp, window_size=86400)  # 1 day

        # Should align to day boundary
        expected_start = datetime(2025, 12, 12, 0, 0, 0, tzinfo=timezone.utc)
        expected_end = datetime(2025, 12, 13, 0, 0, 0, tzinfo=timezone.utc)

        assert start == expected_start
        assert end == expected_end

    def test_calculate_window_bounds_small_window(self) -> None:
        """Test calculation with small window size."""
        timestamp = datetime(2025, 12, 12, 10, 30, 45, tzinfo=timezone.utc)
        start, end = calculate_window_bounds(timestamp, window_size=10)  # 10 seconds

        # Should align to 10-second boundary
        expected_start = datetime(2025, 12, 12, 10, 30, 40, tzinfo=timezone.utc)
        expected_end = datetime(2025, 12, 12, 10, 30, 50, tzinfo=timezone.utc)

        assert start == expected_start
        assert end == expected_end

    def test_calculate_window_bounds_end_minus_start_equals_window_size(
        self,
    ) -> None:
        """Test window duration equals window_size."""
        timestamp = datetime(2025, 12, 12, 10, 30, 45, tzinfo=timezone.utc)
        window_size = 120

        start, end = calculate_window_bounds(timestamp, window_size=window_size)

        duration = (end - start).total_seconds()
        assert duration == window_size


__all__: list[str] = []
