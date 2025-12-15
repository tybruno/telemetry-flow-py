"""Message deserialization for telemetry events.

This module provides message parsing and validation, converting raw stream
data into structured TelemetryEvent domain models.

Classes:
    MessageDeserializer: Deserializes raw stream data to TelemetryEvent.
"""

import logging as _log
import math
from datetime import datetime, timezone
from typing import Any

from src.consumers.exceptions import DeserializationError
from src.core.models import TelemetryEvent


class MessageDeserializer:
    """Deserializes raw stream messages to TelemetryEvent objects.

    Handles parsing, type conversion, and validation of raw message data
    from the stream into structured TelemetryEvent domain models.

    Attributes:
        This class has no instance attributes. All methods are stateless.

    Example:
        deserializer = MessageDeserializer()

        raw_data = {
            "device_id": "router-01",
            "interface": "eth0",
            "metric_name": "bandwidth_utilization",
            "metric_value": "85.5",
            "timestamp": "2025-12-12T10:30:00Z"
        }

        try:
            event = deserializer.deserialize(raw_data)
            print(f"Parsed: {event.device_id}")
        except DeserializationError as e:
            _log.error("Failed to parse: %s", e)
    """

    def deserialize(self, data: dict[str, Any]) -> TelemetryEvent:
        """Deserialize raw message data to TelemetryEvent.

        Args:
            data: Raw message dictionary from stream.

        Returns:
            Parsed and validated TelemetryEvent.

        Raises:
            DeserializationError: If data is invalid or cannot be parsed.

        Example:
            event = deserializer.deserialize({
                "device_id": "router-01",
                "interface": "eth0",
                "metric_name": "bandwidth",
                "metric_value": "95.5",
                "timestamp": "2025-12-12T10:00:00Z"
            })
        """
        try:
            fields = self._extract_required_fields(data)

            metric_value = self._parse_metric_value(fields["metric_value_str"])
            timestamp = self._parse_timestamp(fields["timestamp_str"])

            event = TelemetryEvent(
                device_id=fields["device_id"],
                interface=fields["interface"],
                metric_name=fields["metric_name"],
                metric_value=metric_value,
                timestamp=timestamp,
            )

            return event

        except DeserializationError:
            raise
        except Exception as e:
            error_message = "Failed to deserialize message: %s"
            _log.error(error_message, str(e))
            raise DeserializationError(error_message % str(e)) from e

    def _extract_required_fields(self, data: dict[str, Any]) -> dict[str, str]:
        """Extract and validate required fields from raw data.

        Args:
            data: Raw message dictionary.

        Returns:
            Dictionary with validated string fields.

        Raises:
            DeserializationError: If required fields are missing.
        """
        device_id = data.get("device_id")
        interface = data.get("interface")
        metric_name = data.get("metric_name")
        metric_value_str = data.get("metric_value")
        timestamp_str = data.get("timestamp")

        all_fields_present = all(
            [device_id, interface, metric_name, metric_value_str, timestamp_str]
        )

        if not all_fields_present:
            missing_fields = self._identify_missing_fields(data)
            error_message = "Missing required fields: %s"
            _log.error(error_message, missing_fields)
            raise DeserializationError(
                error_message % ", ".join(missing_fields)
            ) from None

        validated_fields = {
            "device_id": str(device_id),
            "interface": str(interface),
            "metric_name": str(metric_name),
            "metric_value_str": str(metric_value_str),
            "timestamp_str": str(timestamp_str),
        }
        return validated_fields

    def _identify_missing_fields(self, data: dict[str, Any]) -> list[str]:
        """Identify which required fields are missing.

        Args:
            data: Raw message dictionary.

        Returns:
            List of missing field names.
        """
        required_fields = [
            "device_id",
            "interface",
            "metric_name",
            "metric_value",
            "timestamp",
        ]

        missing_fields = [field for field in required_fields if not data.get(field)]

        return missing_fields

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """Parse ISO format timestamp string.

        Args:
            ts_str: ISO format timestamp string.

        Returns:
            Parsed datetime object.

        Raises:
            DeserializationError: If timestamp format is invalid.
        """
        try:
            # Try parsing with fromisoformat (handles ISO 8601)
            # Replace Z with +00:00 for Python's fromisoformat
            if ts_str.endswith("Z"):
                ts_str = ts_str[:-1] + "+00:00"

            parsed_timestamp = datetime.fromisoformat(ts_str)

            # Ensure timezone aware
            if parsed_timestamp.tzinfo is None:
                parsed_timestamp = parsed_timestamp.replace(tzinfo=timezone.utc)

            return parsed_timestamp
        except Exception as e:
            error_message = "Invalid timestamp format: %s"
            _log.error(error_message, str(e))
            raise DeserializationError(error_message % str(e)) from e

    def _parse_metric_value(self, value_str: str) -> float:
        """Parse metric value string to float.

        Args:
            value_str: String representation of metric value.

        Returns:
            Parsed float value.

        Raises:
            DeserializationError: If value cannot be parsed to float.
        """
        try:
            parsed_value = float(value_str)

            if not math.isfinite(parsed_value):
                error_message = "Metric value must be finite: %s"
                _log.error(error_message, value_str)
                raise DeserializationError(error_message % value_str) from None

            return parsed_value
        except ValueError as e:
            error_message = "Invalid metric value format: %s"
            _log.error(error_message, str(e))
            raise DeserializationError(error_message % str(e)) from e


__all__ = ["MessageDeserializer"]
