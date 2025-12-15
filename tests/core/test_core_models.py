"""Tests for core models."""

from datetime import datetime, timezone

import pytest

from src.core.models import TelemetryEvent


class TestTelemetryEvent:
    """Test suite for TelemetryEvent dataclass."""

    @pytest.fixture
    def sample_timestamp(self) -> datetime:
        """Create sample timestamp.

        Returns:
            UTC datetime instance.
        """
        timestamp = datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)
        return timestamp

    def test_telemetry_event_creation(self, sample_timestamp: datetime) -> None:
        """Test TelemetryEvent creation with all fields.

        Args:
            sample_timestamp: Sample timestamp fixture.
        """
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth_utilization",
            metric_value=85.5,
            timestamp=sample_timestamp,
        )

        assert event.device_id == "router-01"
        assert event.interface == "eth0"
        assert event.metric_name == "bandwidth_utilization"
        assert event.metric_value == 85.5
        assert event.timestamp == sample_timestamp

    def test_telemetry_event_is_frozen(self, sample_timestamp: datetime) -> None:
        """Test TelemetryEvent is immutable.

        Args:
            sample_timestamp: Sample timestamp fixture.
        """
        event = TelemetryEvent(
            device_id="switch-01",
            interface="port-1",
            metric_name="packet_loss",
            metric_value=0.02,
            timestamp=sample_timestamp,
        )

        with pytest.raises(Exception):
            event.device_id = "router-02"  # type: ignore[misc]

    def test_telemetry_event_uses_slots(self) -> None:
        """Test TelemetryEvent uses __slots__ for memory efficiency."""
        slots_defined = hasattr(TelemetryEvent, "__slots__")
        assert slots_defined

    def test_telemetry_event_requires_keyword_arguments(
        self,
        sample_timestamp: datetime,
    ) -> None:
        """Test TelemetryEvent requires keyword-only arguments.

        Args:
            sample_timestamp: Sample timestamp fixture.
        """
        # Keyword arguments should work
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=50.0,
            timestamp=sample_timestamp,
        )
        assert event.device_id == "router-01"

        # Positional arguments should fail
        with pytest.raises(TypeError):
            TelemetryEvent(  # type: ignore[misc]
                "router-01",
                "eth0",
                "cpu",
                50.0,
                sample_timestamp,
            )

    @pytest.mark.parametrize(
        ("metric_name", "metric_value"),
        [
            ("bandwidth_utilization", 85.5),
            ("packet_loss", 0.02),
            ("latency_ms", 12.3),
            ("cpu_usage", 95.0),
            ("memory_usage", 78.5),
        ],
    )
    def test_telemetry_event_different_metrics(
        self,
        metric_name: str,
        metric_value: float,
        sample_timestamp: datetime,
    ) -> None:
        """Test TelemetryEvent with different metric types.

        Args:
            metric_name: Name of metric.
            metric_value: Value of metric.
            sample_timestamp: Sample timestamp fixture.
        """
        event = TelemetryEvent(
            device_id="device-01",
            interface="if-0",
            metric_name=metric_name,
            metric_value=metric_value,
            timestamp=sample_timestamp,
        )

        assert event.metric_name == metric_name
        assert event.metric_value == metric_value

    def test_telemetry_event_equality(self, sample_timestamp: datetime) -> None:
        """Test TelemetryEvent equality comparison.

        Args:
            sample_timestamp: Sample timestamp fixture.
        """
        event1 = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=50.0,
            timestamp=sample_timestamp,
        )

        event2 = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=50.0,
            timestamp=sample_timestamp,
        )

        assert event1 == event2

    def test_telemetry_event_different_values_not_equal(
        self,
        sample_timestamp: datetime,
    ) -> None:
        """Test events with different values are not equal.

        Args:
            sample_timestamp: Sample timestamp fixture.
        """
        event1 = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=50.0,
            timestamp=sample_timestamp,
        )

        event2 = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=75.0,  # Different value
            timestamp=sample_timestamp,
        )

        assert event1 != event2

    def test_telemetry_event_with_integer_value(
        self,
        sample_timestamp: datetime,
    ) -> None:
        """Test TelemetryEvent accepts integer metric values.

        Args:
            sample_timestamp: Sample timestamp fixture.
        """
        event = TelemetryEvent(
            device_id="switch-01",
            interface="port-1",
            metric_name="error_count",
            metric_value=42,  # Integer value
            timestamp=sample_timestamp,
        )

        assert event.metric_value == 42

    def test_telemetry_event_with_zero_value(
        self,
        sample_timestamp: datetime,
    ) -> None:
        """Test TelemetryEvent with zero metric value.

        Args:
            sample_timestamp: Sample timestamp fixture.
        """
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="errors",
            metric_value=0.0,
            timestamp=sample_timestamp,
        )

        assert event.metric_value == 0.0

    def test_telemetry_event_with_negative_value(
        self,
        sample_timestamp: datetime,
    ) -> None:
        """Test TelemetryEvent with negative metric value.

        Args:
            sample_timestamp: Sample timestamp fixture.
        """
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="signal_strength",
            metric_value=-45.2,
            timestamp=sample_timestamp,
        )

        assert event.metric_value == -45.2


__all__: list[str] = []
