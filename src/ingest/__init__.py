"""Telemetry ingest service for receiving and forwarding events.

Service:
    IngestService: Core ingest service for receiving telemetry
    create_app: FastAPI application factory

Models:
    IngestRequest: HTTP request model for telemetry ingestion
    IngestResponse: HTTP response model
    HealthResponse: Health check response model

Exceptions:
    IngestError: Base exception for ingest errors
    InvalidPayloadError: Invalid payload validation errors
    StreamPublishError: Stream publishing failures
    ServiceUnavailableError: Service unavailability errors
"""

from src.ingest.api import router
from src.ingest.exceptions import (
    IngestError,
    InvalidPayloadError,
    ServiceUnavailableError,
    StreamPublishError,
)
from src.ingest.main import create_app, main
from src.ingest.models import HealthResponse, IngestRequest, IngestResponse
from src.ingest.service import IngestService

__all__ = [
    "HealthResponse",
    "IngestError",
    "IngestRequest",
    "IngestResponse",
    "IngestService",
    "InvalidPayloadError",
    "ServiceUnavailableError",
    "StreamPublishError",
    "create_app",
    "main",
    "router",
]
