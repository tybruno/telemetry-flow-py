"""FastAPI HTTP endpoints for telemetry ingest service.

This module defines the HTTP API endpoints for receiving telemetry
data and health checks.

Functions:
    ingest_telemetry: POST endpoint for telemetry ingestion.
    health_check: GET endpoint for service health.

Example:
    Running the API::

        import uvicorn
        from src.ingest.api import app

        uvicorn.run(app, host="0.0.0.0", port=8000)
"""

import logging as _log

from fastapi import APIRouter, Depends, HTTPException, status

from src.ingest.dependencies import get_ingest_service
from src.ingest.exceptions import InvalidPayloadError, StreamPublishError
from src.ingest.models import HealthResponse, IngestRequest, IngestResponse
from src.ingest.service import IngestService

router = APIRouter(prefix="/api/v1", tags=["telemetry"])

# Dependency singletons
_ingest_service_dependency = Depends(get_ingest_service)


@router.post(
    "/telemetry",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest telemetry data",
    description="Receive and process network device telemetry data",
)
async def ingest_telemetry(
    request: IngestRequest,
    service: IngestService = _ingest_service_dependency,
) -> IngestResponse:
    """Ingest telemetry data from network devices.

    Receives telemetry data via HTTP POST, validates it, and publishes
    to the telemetry stream for processing.

    Args:
        request: Telemetry data payload.
        service: Injected ingest service instance.

    Returns:
        IngestResponse with event ID and status.

    Raises:
        HTTPException: 400 for invalid payload, 503 for service unavailable.

    Example:
        Request body::

            {
                "device_id": "router-01",
                "interface": "eth0",
                "metric_name": "bandwidth_utilization",
                "metric_value": 85.5,
                "timestamp": "2024-12-12T10:30:00Z"
            }

        Response::

            {
                "event_id": "msg-12345",
                "status": "success",
                "device_id": "router-01"
            }
    """
    try:
        response = await service.ingest_telemetry(request)

        _log.info(
            "Telemetry ingested: event_id=%s, device=%s",
            response.event_id,
            request.device_id,
        )

        return response

    except InvalidPayloadError as e:
        _log.warning("Invalid telemetry payload: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    except StreamPublishError as e:
        _log.error("Failed to publish telemetry: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable",
        ) from e


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check service health and dependencies",
)
async def health_check(
    service: IngestService = _ingest_service_dependency,
) -> HealthResponse:
    """Check health of ingest service and dependencies.

    Returns health status including Redis connectivity and uptime.

    Args:
        service: Injected ingest service instance.

    Returns:
        HealthResponse with service status.

    Example:
        Response::

            {
                "status": "healthy",
                "redis_connected": true,
                "uptime_seconds": 3600.5
            }
    """
    is_healthy = await service.check_health()
    uptime = service.get_uptime_seconds()

    response = HealthResponse(
        status="healthy" if is_healthy else "unhealthy",
        redis_connected=is_healthy,
        uptime_seconds=uptime,
    )

    return response


__all__ = [
    "health_check",
    "ingest_telemetry",
    "router",
]
