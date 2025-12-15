"""Tests for message deserializer functionality.

Tests the MessageDeserializer class including parsing, validation,
and error handling for malformed messages.
"""

from datetime import datetime, timezone
from typing import Any

import pytest

from src.consumers.deserializer import MessageDeserializer
from src.consumers.exceptions import DeserializationError
from src.core.models import TelemetryEvent


class TestMessageDeserializer:
    """Tests for MessageDeserializer class."""

    @pytest.fixture
    def deserializer(self) -> MessageDeserializer:
        """Create deserializer instance.

        Returns:
            MessageDeserializer instance.
        """
        return MessageDeserializer()

    @pytest.fixture
    def valid_message(self) -> dict[str, Any]:
        """Create valid message data.

        Returns:
            Valid message dictionary.
        """
        message: dict[str, Any] = {
            "device_id": "router-01",
            "interface": "eth0",
            "metric_name": "bandwidth_utilization",
            "metric_value": "85.5",
            "timestamp": "2025-12-12T10:30:00Z",
        }
        return message

    def test_deserialize_valid_message(
        self,
        deserializer: MessageDeserializer,
        valid_message: dict[str, Any],
    ) -> None:
        """Test deserializer parses valid message data.

        Verifies deserializer converts raw dict to TelemetryEvent
        with correct field mapping.

        Args:
            deserializer: MessageDeserializer fixture.
            valid_message: Valid message fixture.
        """
        event = deserializer.deserialize(valid_message)

        assert isinstance(event, TelemetryEvent)
        assert event.device_id == "router-01"
        assert event.interface == "eth0"
        assert event.metric_name == "bandwidth_utilization"
        assert event.metric_value == 85.5
        assert event.timestamp == datetime(2025, 12, 12, 10, 30, 0, tzinfo=timezone.utc)

    @pytest.mark.parametrize(
        "missing_field",
        ["device_id", "interface", "metric_name", "metric_value", "timestamp"],
    )
    def test_deserialize_missing_field_raises(
        self,
        deserializer: MessageDeserializer,
        valid_message: dict[str, Any],
        missing_field: str,
    ) -> None:
        """Test deserializer raises when required field missing.

        Args:
            deserializer: MessageDeserializer fixture.
            valid_message: Valid message fixture.
            missing_field: Field to remove.
        """
        del valid_message[missing_field]

        with pytest.raises(DeserializationError, match="Missing required fields"):
            deserializer.deserialize(valid_message)

    def test_deserialize_malformed_message(
        self,
        deserializer: MessageDeserializer,
    ) -> None:
        """Test deserializer raises on malformed data.

        Verifies DeserializationError raised when data structure
        doesn't match expected format.

        Args:
            deserializer: MessageDeserializer fixture.
        """
        malformed_data = {
            "device_id": "router-01",
            "interface": "eth0",
            "metric_name": "bandwidth",
            "metric_value": "not_a_number",
            "timestamp": "2025-12-12T10:30:00Z",
        }

        with pytest.raises(DeserializationError, match="Invalid metric value format"):
            deserializer.deserialize(malformed_data)

    def test_validate_required_fields(
        self,
        deserializer: MessageDeserializer,
    ) -> None:
        """Test deserializer validates required fields present.

        Verifies ValidationError raised when required fields missing.

        Args:
            deserializer: MessageDeserializer fixture.
        """
        incomplete_data = {
            "device_id": "router-01",
            "interface": "eth0",
        }

        with pytest.raises(DeserializationError, match="Missing required fields"):
            deserializer.deserialize(incomplete_data)

    @pytest.mark.parametrize(
        "invalid_timestamp",
        ["invalid_date", "2025-13-45", "not a timestamp"],
    )
    def test_deserialize_invalid_timestamp_raises(
        self,
        deserializer: MessageDeserializer,
        valid_message: dict[str, Any],
        invalid_timestamp: str,
    ) -> None:
        """Test invalid timestamp raises DeserializationError.

        Args:
            deserializer: MessageDeserializer fixture.
            valid_message: Valid message fixture.
            invalid_timestamp: Invalid timestamp string.
        """
        valid_message["timestamp"] = invalid_timestamp

        with pytest.raises(DeserializationError, match="Invalid timestamp format"):
            deserializer.deserialize(valid_message)

    @pytest.mark.parametrize(
        ("metric_value", "expected"),
        [
            ("85.5", 85.5),
            ("0", 0.0),
            ("100", 100.0),
            ("-45.2", -45.2),
            ("0.001", 0.001),
        ],
    )
    def test_parse_metric_value_valid(
        self,
        deserializer: MessageDeserializer,
        valid_message: dict[str, Any],
        metric_value: str,
        expected: float,
    ) -> None:
        """Test parsing various valid metric values.

        Args:
            deserializer: MessageDeserializer fixture.
            valid_message: Valid message fixture.
            metric_value: Metric value string.
            expected: Expected parsed value.
        """
        valid_message["metric_value"] = metric_value
        event = deserializer.deserialize(valid_message)
        assert event.metric_value == expected

    @pytest.mark.parametrize(
        "invalid_value",
        ["inf", "-inf", "nan", "NaN"],
    )
    def test_parse_metric_value_non_finite_raises(
        self,
        deserializer: MessageDeserializer,
        valid_message: dict[str, Any],
        invalid_value: str,
    ) -> None:
        """Test non-finite metric values raise error.

        Args:
            deserializer: MessageDeserializer fixture.
            valid_message: Valid message fixture.
            invalid_value: Non-finite value string.
        """
        valid_message["metric_value"] = invalid_value

        with pytest.raises(DeserializationError, match="Metric value must be finite"):
            deserializer.deserialize(valid_message)

    def test_deserialize_adds_utc_timezone(
        self,
        deserializer: MessageDeserializer,
        valid_message: dict[str, Any],
    ) -> None:
        """Test timestamp without timezone gets UTC added.

        Args:
            deserializer: MessageDeserializer fixture.
            valid_message: Valid message fixture.
        """
        # Timestamp without Z
        valid_message["timestamp"] = "2025-12-12T10:30:00"
        event = deserializer.deserialize(valid_message)

        assert event.timestamp.tzinfo is not None

    def test_deserialize_handles_iso_format_variations(
        self,
        deserializer: MessageDeserializer,
        valid_message: dict[str, Any],
    ) -> None:
        """Test various ISO 8601 timestamp formats.

        Args:
            deserializer: MessageDeserializer fixture.
            valid_message: Valid message fixture.
        """
        timestamps = [
            "2025-12-12T10:30:00Z",
            "2025-12-12T10:30:00+00:00",
            "2025-12-12T10:30:00.123456Z",
        ]

        for ts in timestamps:
            valid_message["timestamp"] = ts
            event = deserializer.deserialize(valid_message)
            assert event.timestamp.year == 2025
            assert event.timestamp.month == 12
            assert event.timestamp.day == 12


__all__: list[str] = []
