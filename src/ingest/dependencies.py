"""FastAPI dependency injection for ingest service.

This module provides dependency injection functions for FastAPI endpoints.
Manages service lifecycle and dependency wiring.

Functions:
    get_stream: Get stream protocol implementation.
    get_ingest_service: Get ingest service instance.

Example:
    Using dependencies in endpoints::

        @router.post("/telemetry")
        async def ingest(
            request: IngestRequest,
            service: IngestService = Depends(get_ingest_service)
        ):
            return await service.ingest_telemetry(request)
"""


from src.core.protocols import StreamProtocol
from src.ingest.service import IngestService

# Global service instance (initialized on startup)
_service_instance: IngestService | None = None


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


__all__ = [
    "get_stream",
    "get_ingest_service",
    "initialize_service",
]
