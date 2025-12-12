"""Message deserialization for telemetry events.

Class:
    MessageDeserializer: Deserializes raw stream data to TelemetryEvent.
"""

from datetime import datetime
from typing import Any

from src.core.models import TelemetryEvent


class MessageDeserializer:
    """Deserializes raw stream messages to TelemetryEvent objects.

    Handles parsing, type conversion, and validation of raw message data
    from the stream into structured TelemetryEvent domain models.

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
        raise NotImplementedError

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """Parse ISO format timestamp string.

        Args:
            ts_str: ISO format timestamp string.

        Returns:
            Parsed datetime object.

        Raises:
            DeserializationError: If timestamp format is invalid.
        """
        raise NotImplementedError

    def _parse_metric_value(self, value_str: str) -> float:
        """Parse metric value string to float.

        Args:
            value_str: String representation of metric value.

        Returns:
            Parsed float value.

        Raises:
            DeserializationError: If value cannot be parsed to float.
        """
        raise NotImplementedError


__all__ = ["MessageDeserializer"]
