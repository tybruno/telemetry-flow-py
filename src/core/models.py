"""Core domain models shared across all services.

This module defines the universal data structures used throughout the
telemetry processing system. These models represent the core business
domain that all services understand and use.

Classes:
    TelemetryEvent: Universal telemetry event structure shared by all
        services.

Example:
    Creating a telemetry event::

        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth_utilization",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc)
        )
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class TelemetryEvent:
    """Universal telemetry event shared across all services.

    This is the core domain model that represents a single telemetry
    measurement from a network device. All services use this model
    to ensure consistent data representation.

    Attributes:
        device_id: Unique identifier for the network device.
        interface: Network interface name (e.g., "eth0", "GigabitEthernet0/0").
        metric_name: Name of the metric being measured.
        metric_value: Numerical value of the metric.
        timestamp: UTC timestamp when the metric was captured.

    Example:
        Creating a telemetry event::

            event = TelemetryEvent(
                device_id="switch-01",
                interface="port-24",
                metric_name="packet_loss",
                metric_value=0.02,
                timestamp=datetime.now(timezone.utc)
            )
    """

    device_id: str
    interface: str
    metric_name: str
    metric_value: float
    timestamp: datetime


__all__ = [
    "TelemetryEvent",
]
