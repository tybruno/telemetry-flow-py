"""FastAPI dependency injection for ingest service.

This module provides dependency injection functions for FastAPI endpoints.
Manages service lifecycle and dependency wiring.

Classes:
    None.

Functions:
    get_stream: Get stream protocol implementation.
    get_ingest_service: Get ingest service instance.
    initialize_service: Initialize service with dependencies.

Example:
    Using dependencies in endpoints::

        @router.post("/telemetry")
        async def ingest(
            request: IngestRequest,
            service: IngestService = Depends(get_ingest_service)
        ):
            return await service.ingest_telemetry(request)
"""

import logging as _log

from src.core.protocols import StreamProtocol
from src.ingest.service import IngestService

# Global service instance (initialized on startup)
_service_instance: IngestService | None = None
_stream_instance: StreamProtocol | None = None


def get_stream() -> StreamProtocol:
    """Get stream protocol implementation.

    Returns the configured stream implementation (Redis Streams).
    This is typically called during application startup.

    Returns:
        StreamProtocol implementation instance.

    Raises:
        RuntimeError: If stream is not initialized.

    Example:
        Getting stream in main::

            stream = get_stream()
    """
    if _stream_instance is None:
        error_message = "Stream not initialized. Call initialize_service first."
        _log.error(error_message)
        raise RuntimeError(error_message) from None

    return _stream_instance


def get_ingest_service() -> IngestService:
    """Get ingest service instance (FastAPI dependency).

    Returns the singleton ingest service instance. Used as a
    FastAPI dependency for endpoint injection.

    Returns:
        IngestService instance.

    Raises:
        RuntimeError: If service not initialized.

    Example:
        Using in endpoint::

            @router.post("/telemetry")
            async def ingest_endpoint(
                service: IngestService = Depends(get_ingest_service)
            ):
                ...
    """
    if _service_instance is None:
        error_message = "Service not initialized. Call initialize_service first."
        _log.error(error_message)
        raise RuntimeError(error_message) from None

    return _service_instance


def initialize_service(stream: StreamProtocol) -> None:
    """Initialize the ingest service with dependencies.

    Called during application startup to wire up dependencies
    and create the service instance.

    Args:
        stream: Stream protocol implementation.

    Example:
        Application startup::

            from src.streams.redis_stream import RedisStream

            stream = RedisStream(url="redis://localhost")
            initialize_service(stream=stream)
    """
    global _service_instance, _stream_instance

    _stream_instance = stream
    _service_instance = IngestService(stream=stream)

    _log.info("Ingest service initialized")


__all__ = [
    "get_ingest_service",
    "get_stream",
    "initialize_service",
]
