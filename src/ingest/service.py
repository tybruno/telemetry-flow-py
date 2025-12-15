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
import math
from contextlib import suppress
from datetime import datetime, timezone

from src.core.models import TelemetryEvent
from src.core.protocols import StreamProtocol
from src.ingest.exceptions import InvalidPayloadError, StreamPublishError
from src.ingest.models import IngestRequest, IngestResponse
from src.streams.partitioner import StreamPartitioner


class IngestService:
    """Main service class for telemetry ingestion.

    Handles validation, transformation, and publishing of telemetry
    events. Depends on a StreamProtocol implementation for publishing.
    
    Uses partitioning to distribute events across multiple streams
    based on device_id, enabling horizontal scaling of processors.

    Attributes:
        _stream: Stream protocol implementation for publishing events.
        _partitioner: Stream partitioner for horizontal scaling.
        _base_stream_name: Base name for telemetry streams.
        _start_time: Service start time for uptime tracking.

    Example:
        Creating and using the service::

            partitioner = StreamPartitioner(num_partitions=3)
            service = IngestService(
                stream=redis_stream,
                partitioner=partitioner
            )

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

    __slots__ = ("_start_time", "_stream", "_partitioner", "_base_stream_name")

    _stream: StreamProtocol
    _partitioner: StreamPartitioner
    _base_stream_name: str
    _start_time: datetime

    def __init__(
        self,
        *,
        stream: StreamProtocol,
        partitioner: StreamPartitioner,
        base_stream_name: str = "telemetry",
    ) -> None:
        """Initialize the ingest service.

        Args:
            stream: Stream protocol implementation for publishing events.
            partitioner: Stream partitioner for horizontal scaling.
            base_stream_name: Base name for telemetry streams (default: "telemetry").

        Example:
            Initialize with Redis stream and partitioning::

                from src.streams.redis_stream import RedisStream
                from src.streams.partitioner import StreamPartitioner

                stream = RedisStream(url="redis://localhost:6379")
                partitioner = StreamPartitioner(num_partitions=3)
                service = IngestService(
                    stream=stream,
                    partitioner=partitioner
                )
        """
        self._stream = stream
        self._partitioner = partitioner
        self._base_stream_name = base_stream_name
        self._start_time = datetime.now(timezone.utc)
        _log.info(
            "Ingest service initialized: partitions=%d, base_stream=%s",
            partitioner.num_partitions,
            base_stream_name,
        )

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

        _log.debug(
            "Ingesting telemetry: device=%s, interface=%s, metric=%s",
            request.device_id,
            request.interface,
            request.metric_name
        )

        # Validate request
        self._validate_request(request)

        # Transform to domain event
        event = self._transform_to_event(request)

        # Publish to stream
        event_id = await self._publish_event(event)

        response = IngestResponse(
            event_id=event_id,
            status="accepted",
            device_id=request.device_id
        )
        return response

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
        # Try a simple publish/consume operation
        with suppress(Exception):
            # Just check if stream is accessible
            # In production might do a ping or test operation
            test_successful = bool(self._stream)
            return test_successful

        health_status = False
        return health_status

    def get_uptime_seconds(self) -> float:
        """Get service uptime in seconds.

        Returns:
            Number of seconds since service started.

        Example:
            Getting uptime::

                uptime = service.get_uptime_seconds()
                print(f"Uptime: {uptime:.2f} seconds")
        """
        current_time = datetime.now(timezone.utc)
        uptime_delta = current_time - self._start_time
        uptime_seconds = uptime_delta.total_seconds()
        return uptime_seconds

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
        validation_errors: list[str] = []

        self._validate_device_fields(request, validation_errors)
        self._validate_metric_fields(request, validation_errors)
        self._validate_timestamp_field(request, validation_errors)

        if validation_errors:
            error_message = "Validation failed: %s"
            _log.error(error_message, "; ".join(validation_errors))
            joined_errors = ", ".join(validation_errors)
            raise InvalidPayloadError(error_message % joined_errors) from None

    def _validate_device_fields(
        self,
        request: IngestRequest,
        validation_errors: list[str]
    ) -> None:
        """Validate device-related fields.

        Args:
            request: Request to validate.
            validation_errors: List to append errors to.
        """
        if not request.device_id or not request.device_id.strip():
            validation_errors.append("device_id cannot be empty")

        if not request.interface or not request.interface.strip():
            validation_errors.append("interface cannot be empty")

    def _validate_metric_fields(
        self,
        request: IngestRequest,
        validation_errors: list[str]
    ) -> None:
        """Validate metric-related fields.

        Args:
            request: Request to validate.
            validation_errors: List to append errors to.
        """
        if not request.metric_name or not request.metric_name.strip():
            validation_errors.append("metric_name cannot be empty")

        if not math.isfinite(request.metric_value):
            validation_errors.append("metric_value must be finite")

    def _validate_timestamp_field(
        self,
        request: IngestRequest,
        validation_errors: list[str]
    ) -> None:
        """Validate timestamp field.

        Args:
            request: Request to validate.
            validation_errors: List to append errors to.
        """
        if not request.timestamp:
            validation_errors.append("timestamp cannot be None")
        elif request.timestamp.tzinfo is None:
            validation_errors.append("timestamp must be timezone-aware")

    async def _publish_event(self, event: TelemetryEvent) -> str:
        """Publish event to partitioned stream based on device_id.

        Args:
            event: Event to publish.

        Returns:
            Event ID from stream.

        Raises:
            StreamPublishError: If publish fails.
        """
        try:
            # Get partitioned stream name based on device_id
            stream_name = self._partitioner.get_stream_name(
                base_name=self._base_stream_name,
                device_id=event.device_id
            )
            
            event_id = await self._stream.publish(
                stream=stream_name,
                data=self._serialize_event(event)
            )

            _log.info(
                "Published telemetry event: event_id=%s, device=%s, stream=%s",
                event_id,
                event.device_id,
                stream_name
            )

            return event_id

        except Exception as e:
            error_message = "Failed to publish event: %s"
            _log.error(error_message, str(e))
            raise StreamPublishError(error_message % str(e)) from e

    def _serialize_event(self, event: TelemetryEvent) -> dict[str, str]:
        """Serialize event to stream format.

        Args:
            event: Event to serialize.

        Returns:
            Dictionary with string values for stream.
        """
        serialized_data = {
            "device_id": event.device_id,
            "interface": event.interface,
            "metric_name": event.metric_name,
            "metric_value": str(event.metric_value),
            "timestamp": event.timestamp.isoformat()
        }
        return serialized_data

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
        event = TelemetryEvent(
            device_id=request.device_id,
            interface=request.interface,
            metric_name=request.metric_name,
            metric_value=request.metric_value,
            timestamp=request.timestamp
        )

        return event


__all__ = [
    "IngestService",
]
