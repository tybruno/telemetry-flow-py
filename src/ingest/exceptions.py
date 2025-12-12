"""Ingest service-specific exceptions.

This module defines all exception types specific to the telemetry
ingest service.

Classes:
    IngestError: Base exception for ingest service errors.
    InvalidPayloadError: Invalid request payload errors.
    StreamPublishError: Stream publication failures.
    ServiceUnavailableError: Service temporarily unavailable.

Example:
    Handling ingest-specific errors::

        try:
            await service.ingest_telemetry(request)
        except InvalidPayloadError as e:
            return JSONResponse(status_code=400, content={"error": str(e)})
        except StreamPublishError as e:
            return JSONResponse(status_code=503, content={"error": str(e)})
"""

from src.core.exceptions import TelemetryError


class IngestError(TelemetryError):
    """Base exception for all ingest service errors.

    All ingest-specific exceptions inherit from this class.

    Example:
        Catching all ingest errors::

            try:
                await ingest_service.process()
            except IngestError as e:
                _log.error("Ingest error: %s", e)
    """


class InvalidPayloadError(IngestError):
    """Invalid request payload error.

    Raised when incoming telemetry data fails validation checks.

    Example:
        Invalid metric value::

            if request.metric_value < 0:
                raise InvalidPayloadError(
                    f"Metric value cannot be negative: {request.metric_value}"
                )
    """


class StreamPublishError(IngestError):
    """Stream publication failure error.

    Raised when publishing to the telemetry stream fails.

    Example:
        Publication failure::

            try:
                await stream.publish("telemetry", data)
            except Exception as err:
                raise StreamPublishError(
                    f"Failed to publish to stream: {err}"
                ) from err
    """


class ServiceUnavailableError(IngestError):
    """Service temporarily unavailable error.

    Raised when the service cannot process requests due to
    downstream dependencies being unavailable.

    Example:
        Redis unavailable::

            if not await check_redis_health():
                raise ServiceUnavailableError(
                    "Redis connection unavailable"
                )
    """


__all__ = [
    "IngestError",
    "InvalidPayloadError",
    "StreamPublishError",
    "ServiceUnavailableError",
]
