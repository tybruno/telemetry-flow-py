"""Ingest service business logic.

This module contains the core business logic for the telemetry ingest
service. It handles validation, transformation, and publishing of
telemetry events to the stream.

Classes:
    IngestService: Main service class for telemetry ingestion.

Example:
    Using the ingest service::

        from src.streams.redis_stream import RedisStream

        stream = RedisStream(url="redis://localhost")
        service = IngestService(stream=stream)

        response = await service.ingest_telemetry(request)
"""

import logging as _log
from datetime import datetime, timezone

from src.core.models import TelemetryEvent
from src.core.protocols import StreamProtocol
from src.ingest.models import IngestRequest, IngestResponse


class IngestService:
    """Main service class for telemetry ingestion.

    Handles validation, transformation, and publishing of telemetry
    events. Depends on a StreamProtocol implementation for publishing.

    Attributes:
        _stream: Stream protocol implementation for publishing events.
        _start_time: Service start time for uptime tracking.

    Example:
        Creating and using the service::

            service = IngestService(stream=redis_stream)

            response = await service.ingest_telemetry(
                IngestRequest(
                    device_id="router-01",
                    interface="eth0",
                    metric_name="bandwidth",
                    metric_value=85.5,
                    timestamp=datetime.now(timezone.utc)
                )
            )
    """

    __slots__ = ("_stream", "_start_time")

    _stream: StreamProtocol
    _start_time: datetime

    def __init__(self, *, stream: StreamProtocol) -> None:
        """Initialize the ingest service.

        Args:
            stream: Stream protocol implementation for publishing events.

        Example:
            Initialize with Redis stream::

                from src.streams.redis_stream import RedisStream

                stream = RedisStream(url="redis://localhost:6379")
                service = IngestService(stream=stream)
        """
        self._stream = stream
        self._start_time = datetime.now(timezone.utc)
        _log.info("Ingest service initialized")

    async def ingest_telemetry(
        self,
        request: IngestRequest,
    ) -> IngestResponse:
        """Ingest and publish a telemetry event.

        Validates the request, transforms it to a TelemetryEvent,
        and publishes to the telemetry stream.

        Args:
            request: Validated telemetry request from HTTP API.

        Returns:
            IngestResponse with event ID and status.

        Raises:
            InvalidPayloadError: If request data is invalid.
            StreamPublishError: If publishing to stream fails.

        Example:
            Ingesting telemetry::

                response = await service.ingest_telemetry(
                    IngestRequest(
                        device_id="switch-01",
                        interface="port-1",
                        metric_name="packet_loss",
                        metric_value=0.02,
                        timestamp=datetime.now(timezone.utc)
                    )
                )
                print(response.event_id)
        """
        raise NotImplementedError

    async def check_health(self) -> bool:
        """Check health of service and dependencies.

        Verifies that the service and its dependencies (Redis stream)
        are operational.

        Returns:
            True if service is healthy, False otherwise.

        Example:
            Health check::

                is_healthy = await service.check_health()
                if not is_healthy:
                    _log.error("Service unhealthy")
        """
        raise NotImplementedError

    def get_uptime_seconds(self) -> float:
        """Get service uptime in seconds.

        Returns:
            Number of seconds since service started.

        Example:
            Getting uptime::

                uptime = service.get_uptime_seconds()
                print(f"Uptime: {uptime:.2f} seconds")
        """
        raise NotImplementedError

    def _validate_request(self, request: IngestRequest) -> None:
        """Validate telemetry request data.

        Args:
            request: Telemetry request to validate.

        Raises:
            InvalidPayloadError: If validation fails.

        Example:
            Validation logic::

                self._validate_request(request)
                # Proceeds if valid, raises if invalid
        """
        raise NotImplementedError

    def _transform_to_event(
        self,
        request: IngestRequest,
    ) -> TelemetryEvent:
        """Transform ingest request to domain event.

        Args:
            request: Validated ingest request.

        Returns:
            TelemetryEvent for publishing to stream.

        Example:
            Transformation::

                event = self._transform_to_event(request)
                # event is now a TelemetryEvent
        """
        raise NotImplementedError


__all__ = [
    "IngestService",
]
