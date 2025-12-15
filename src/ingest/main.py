"""Ingest service application entry point.

This module provides the main entry point for the telemetry ingest
service, which receives HTTP POST requests from devices/simulators and
publishes events to Redis Streams for processing.

Architecture:
    - HTTP API (FastAPI) on port 8000
    - Validates incoming telemetry data
    - Publishes to Redis Streams ("telemetry" stream)
    - Returns message ID acknowledgment

Communication:
    Input: HTTP POST /telemetry from devices
    Output: Publishes to Redis Streams for processor consumption

Functions:
    create_app: Create and configure FastAPI application.
    startup_event: Initialize Redis connections and services.
    shutdown_event: Clean shutdown of resources.
    main: Entry point for running the service.

Example:
    Running the service::

        # Via Python module (recommended)
        python -m src.ingest

        # Direct module execution
        python -m src.ingest.main

        # Console script (after pip install -e .)
        telemetry-ingest

        # Via Docker Compose
        docker-compose up ingest

        # Service listens on http://localhost:8000
        # POST to http://localhost:8000/telemetry
"""

import logging as _log
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.protocols import StreamProtocol
from src.ingest.api import router
from src.ingest.dependencies import initialize_service
from src.streams.partitioner import StreamPartitioner
from src.streams.redis_stream import RedisStream

# Environment configuration (loaded at module level)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
NUM_PARTITIONS = int(os.getenv("NUM_PARTITIONS", "3"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifespan events.

    Handles startup and shutdown of resources using modern
    async context manager pattern.

    Args:
        app: FastAPI application instance.

    Yields:
        None during application runtime.
    """
    # Startup: Initialize dependencies
    _log.info("Starting ingest service...")

    # Get Redis URL and partition config from app state
    redis_url = getattr(app.state, "redis_url", REDIS_URL)
    num_partitions = getattr(app.state, "num_partitions", NUM_PARTITIONS)

    # Initialize Redis stream
    stream = RedisStream(url=redis_url)
    app.state.stream = stream
    _log.info("Redis stream initialized: url=%s", redis_url)

    # Initialize stream partitioner for horizontal scaling
    partitioner = StreamPartitioner(num_partitions=num_partitions)
    app.state.partitioner = partitioner
    _log.info("Stream partitioner initialized: partitions=%d", num_partitions)

    # Initialize service dependencies
    initialize_service(stream=cast(StreamProtocol, stream), partitioner=partitioner)
    _log.info("Ingest service dependencies initialized")

    yield

    # Shutdown: Clean up resources
    _log.info("Shutting down ingest service...")

    # Close Redis connection if exists
    if app.state.stream is not None:
        try:
            await app.state.stream.close()
            _log.info("Redis connection closed")
        except Exception as e:
            _log.error("Error closing Redis connection: %s", str(e))

    _log.info("Ingest service shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Initializes the FastAPI application, registers routers,
    and configures middleware and dependencies.

    Returns:
        Configured FastAPI application instance.

    Example:
        Creating app for testing::

            app = create_app()
            client = TestClient(app)
    """
    app = FastAPI(
        title="Telemetry Ingest Service",
        description="HTTP API for ingesting network device telemetry data",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(router)

    _log.info("FastAPI application created")

    return app


def main() -> int:
    """Main entry point for the ingest service.

    Loads configuration from environment variables and config files,
    creates the FastAPI app with all dependencies, and starts the
    uvicorn ASGI server.

    Configuration:
        - INGEST_API_HOST: Host to bind (default: 0.0.0.0)
        - INGEST_API_PORT: Port to bind (default: 8000)
        - REDIS_URL: Redis connection URL (required)

    Services Started:
        - FastAPI HTTP server (uvicorn)
        - Redis Streams connection
        - IngestService with dependency injection

    Returns:
        Exit code:
            - 0: Success - service shutdown cleanly
            - 1: Configuration error - missing or invalid configuration
            - 2: Connection error - failed to connect to Redis
            - 3: Runtime error - unexpected error during operation

    Example:
        Running the service::

            # With defaults (recommended)
            python -m src.ingest

            # Or with console script
            telemetry-ingest

            # With custom port
            INGEST_API_PORT=9000 python -m src.ingest

            # Service available at http://localhost:8000/telemetry
    """
    # Configure logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging_numeric_level = getattr(_log, log_level.upper(), _log.INFO)

    _log.basicConfig(
        level=logging_numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _log.info("Starting telemetry ingest service")

    try:
        # Load configuration from environment
        host = os.getenv("INGEST_API_HOST", "0.0.0.0")
        port = int(os.getenv("INGEST_API_PORT", "8000"))
        redis_url = os.getenv("REDIS_URL")

        if not redis_url:
            error_message = "REDIS_URL environment variable is required"
            _log.error(error_message)
            return 1

        _log.info("Configuration: host=%s, port=%d, redis=%s", host, port, redis_url)

        # Create FastAPI application
        app = create_app()

        # Store redis_url in app state for lifespan to use
        app.state.redis_url = redis_url

        # Run uvicorn server
        _log.info("Starting uvicorn server on %s:%d", host, port)
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level.lower(),
            access_log=True,
        )

        _log.info("Ingest service shutdown cleanly")
        return 0

    except ValueError as e:
        # Configuration error
        _log.error("Configuration error: %s", str(e))
        return 1

    except ConnectionError as e:
        # Connection error
        _log.error("Connection error: %s", str(e))
        return 2

    except KeyboardInterrupt:
        _log.info("Ingest service interrupted by user")
        return 0

    except Exception as e:
        # Runtime error
        _log.error("Ingest service failed: %s", str(e))
        return 3


if __name__ == "__main__":
    sys.exit(main())
__all__ = [
    "create_app",
    "main",
]
