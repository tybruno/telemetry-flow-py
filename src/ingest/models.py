"""Ingest service-specific data models.

This module defines the data structures specific to the telemetry
ingest service, including HTTP request/response models.

Classes:
    IngestRequest: HTTP request payload for telemetry ingestion.
    IngestResponse: HTTP response for successful ingestion.
    HealthResponse: Health check endpoint response.

Example:
    Creating an ingest request::

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc)
        )
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class IngestRequest:
    """HTTP request payload for telemetry ingestion.

    Represents the structure of telemetry data received via HTTP API.
    This model is validated and transformed into a TelemetryEvent.

    Attributes:
        device_id: Unique identifier for the network device.
        interface: Network interface name.
        metric_name: Name of the metric being reported.
        metric_value: Numerical value of the metric.
        timestamp: UTC timestamp when metric was captured.

    Example:
        Creating from JSON payload::

            request = IngestRequest(
                device_id="switch-01",
                interface="GigabitEthernet0/1",
                metric_name="cpu_utilization",
                metric_value=78.5,
                timestamp=datetime.now(timezone.utc)
            )
    """

    device_id: str
    interface: str
    metric_name: str
    metric_value: float
    timestamp: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class IngestResponse:
    """HTTP response for successful telemetry ingestion.

    Returned to clients after successfully ingesting telemetry data.

    Attributes:
        event_id: Unique identifier assigned to the ingested event.
        status: Status of the ingestion (success, queued, etc.).
        device_id: Echo of the device ID for correlation.

    Example:
        Creating a success response::

            response = IngestResponse(
                event_id="msg-12345",
                status="success",
                device_id="router-01"
            )
    """

    event_id: str
    status: str
    device_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class HealthResponse:
    """Health check endpoint response.

    Indicates the health status of the ingest service and its dependencies.

    Attributes:
        status: Overall health status (healthy, degraded, unhealthy).
        redis_connected: Whether Redis connection is healthy.
        uptime_seconds: Service uptime in seconds.

    Example:
        Creating a health response::

            response = HealthResponse(
                status="healthy",
                redis_connected=True,
                uptime_seconds=3600
            )
    """

    status: str
    redis_connected: bool
    uptime_seconds: float


__all__ = [
    "HealthResponse",
    "IngestRequest",
    "IngestResponse",
]
