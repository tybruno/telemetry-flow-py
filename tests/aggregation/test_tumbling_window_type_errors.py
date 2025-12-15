"""Tests for TumblingWindow type validation edge cases."""

from datetime import datetime, timezone

import pytest

from src.aggregation.tumbling_window import TumblingWindowAggregator
from src.core.models import TelemetryEvent


class TestAccumulateEventTypeErrors:
    """Test type error handling in _accumulate_event method."""

    def test_accumulate_with_invalid_values_type_raises(self) -> None:
        """Test accumulate raises TypeError when values is not a list."""
        aggregator = TumblingWindowAggregator(window_size=60)

        # Create a window with invalid values type
        window = {
            "values": "not_a_list",  # Should be list
            "sum": 0.0,
            "count": 0,
            "min": float("inf"),
            "max": float("-inf"),
        }

        event = TelemetryEvent(
            device_id="device-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(TypeError) as exc_info:
            aggregator._accumulate_event(window, event)

        assert "Expected list for values" in str(exc_info.value)

    def test_accumulate_with_invalid_sum_type_raises(self) -> None:
        """Test accumulate raises TypeError when sum is not numeric."""
        aggregator = TumblingWindowAggregator(window_size=60)

        window = {
            "values": [],
            "sum": "not_numeric",  # Should be int or float
            "count": 0,
            "min": float("inf"),
            "max": float("-inf"),
        }

        event = TelemetryEvent(
            device_id="device-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(TypeError) as exc_info:
            aggregator._accumulate_event(window, event)

        assert "Invalid sum type" in str(exc_info.value)

    def test_accumulate_with_invalid_count_type_raises(self) -> None:
        """Test accumulate raises TypeError when count is not int."""
        aggregator = TumblingWindowAggregator(window_size=60)

        window = {
            "values": [],
            "sum": 0.0,
            "count": 0.5,  # Should be int, not float
            "min": float("inf"),
            "max": float("-inf"),
        }

        event = TelemetryEvent(
            device_id="device-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(TypeError) as exc_info:
            aggregator._accumulate_event(window, event)

        assert "Invalid count type" in str(exc_info.value)

    def test_accumulate_with_invalid_min_type_raises(self) -> None:
        """Test accumulate raises TypeError when min is not numeric."""
        aggregator = TumblingWindowAggregator(window_size=60)

        window = {
            "values": [],
            "sum": 0.0,
            "count": 0,
            "min": "not_numeric",  # Should be int or float
            "max": float("-inf"),
        }

        event = TelemetryEvent(
            device_id="device-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(TypeError) as exc_info:
            aggregator._accumulate_event(window, event)

        assert "Invalid min type" in str(exc_info.value)

    def test_accumulate_with_invalid_max_type_raises(self) -> None:
        """Test accumulate raises TypeError when max is not numeric."""
        aggregator = TumblingWindowAggregator(window_size=60)

        window = {
            "values": [],
            "sum": 0.0,
            "count": 0,
            "min": float("inf"),
            "max": None,  # Should be int or float
        }

        event = TelemetryEvent(
            device_id="device-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(TypeError) as exc_info:
            aggregator._accumulate_event(window, event)

        assert "Invalid max type" in str(exc_info.value)


class TestExtractWindowValuesTypeErrors:
    """Test type error handling in _extract_window_values method."""

    def test_extract_window_values_with_non_list_raises(self) -> None:
        """Test _extract_window_values raises TypeError for non-list values."""
        aggregator = TumblingWindowAggregator(window_size=60)

        window = {"values": "not_a_list"}

        with pytest.raises(TypeError, match="Expected list for values"):
            aggregator._extract_window_values(window)


class TestCreateWindowBoundsTypeErrors:
    """Test type error handling in _create_window_bounds method."""

    def test_create_window_bounds_with_invalid_start_type_raises(self) -> None:
        """Test _create_window_bounds raises TypeError for invalid start."""
        aggregator = TumblingWindowAggregator(window_size=60)

        window = {
            "start": "not_a_datetime",  # Should be datetime
            "end": datetime.now(timezone.utc),
            "device_id": "device-01",
            "interface": "eth0",
            "metric_name": "bandwidth",
        }

        with pytest.raises(TypeError, match="Expected datetime for start"):
            aggregator._create_window_bounds(window, ("device-01", "eth0", "bandwidth"))

    def test_create_window_bounds_with_invalid_end_type_raises(self) -> None:
        """Test _create_window_bounds raises TypeError for invalid end."""
        aggregator = TumblingWindowAggregator(window_size=60)

        now = datetime.now(timezone.utc)
        window = {
            "start": now,
            "end": "not_a_datetime",  # Should be datetime
            "device_id": "device-01",
            "interface": "eth0",
            "metric_name": "bandwidth",
        }

        with pytest.raises(TypeError, match="Expected datetime for end"):
            aggregator._create_window_bounds(window, ("device-01", "eth0", "bandwidth"))


__all__ = [
    "TestAccumulateEventTypeErrors",
    "TestExtractWindowValuesTypeErrors",
    "TestCreateWindowBoundsTypeErrors",
]
