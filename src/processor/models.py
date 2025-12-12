"""Processor service-specific telemetry models.

This module contains telemetry-specific models used only by the processor
service for orchestrating telemetry event processing. Generic aggregation
and detection models are in their respective libraries.

Classes:
    TelemetryWindowKey: Unique identifier for telemetry aggregation windows
    TelemetryMetricIdentifier: Identifies specific telemetry metrics

Example:
    Creating a window key::

        key = TelemetryWindowKey(
            device_id="router-01",
            interface="GigabitEthernet0/1",
            metric_name="cpu_utilization"
        )
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class TelemetryWindowKey:
    """Unique identifier for telemetry aggregation windows.

    Combines device, interface, and metric to create a unique key for
    tracking separate aggregation windows for each telemetry metric stream.

    Attributes:
        device_id: Unique device identifier (e.g., "router-01")
        interface: Network interface identifier (e.g., "GigabitEthernet0/1")
        metric_name: Name of the metric being tracked (e.g., "cpu_utilization")

    Example:
        key = TelemetryWindowKey(
            device_id="router-01",
            interface="GigabitEthernet0/1",
            metric_name="bandwidth_utilization"
        )

        # Use as dictionary key
        windows[key] = window_state
    """
    device_id: str
    interface: str
    metric_name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class TelemetryMetricIdentifier:
    """Identifies a specific telemetry metric.

    Lightweight identifier for telemetry metrics used in configuration
    and threshold management.

    Attributes:
        metric_name: Name of the metric (e.g., "cpu_utilization")
        metric_type: Type/category of metric (e.g., "utilization", "counter")
        unit: Unit of measurement (e.g., "percent", "bps")

    Example:
        identifier = TelemetryMetricIdentifier(
            metric_name="cpu_utilization",
            metric_type="utilization",
            unit="percent"
        )
    """
    metric_name: str
    metric_type: str
    unit: str | None = None


__all__ = ["TelemetryWindowKey", "TelemetryMetricIdentifier"]
