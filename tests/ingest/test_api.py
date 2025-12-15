"""Tests for FastAPI endpoints in ingest API."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.ingest.api import health_check, ingest_telemetry
from src.ingest.exceptions import InvalidPayloadError, StreamPublishError
from src.ingest.models import IngestRequest, IngestResponse


class TestIngestTelemetry:
    """Test ingest_telemetry endpoint."""

    @pytest.mark.asyncio
    async def test_ingest_telemetry_success(self) -> None:
        """Test successful telemetry ingestion."""
        mock_service = MagicMock()
        mock_response = IngestResponse(
            event_id="msg-12345",
            status="accepted",
            device_id="router-01",
        )
        mock_service.ingest_telemetry = AsyncMock(return_value=mock_response)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth_utilization",
            metric_value=85.5,
            timestamp=datetime(2024, 12, 12, 10, 30, 0, tzinfo=timezone.utc),
        )

        response = await ingest_telemetry(request, service=mock_service)

        assert response.event_id == "msg-12345"
        assert response.status == "accepted"
        assert response.device_id == "router-01"
        mock_service.ingest_telemetry.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_ingest_telemetry_logs_success(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test successful ingestion logs info message."""
        import logging

        mock_service = MagicMock()
        mock_response = IngestResponse(
            event_id="msg-12345",
            status="accepted",
            device_id="router-01",
        )
        mock_service.ingest_telemetry = AsyncMock(return_value=mock_response)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with caplog.at_level(logging.INFO):
            await ingest_telemetry(request, service=mock_service)

        log_messages = [record.message for record in caplog.records]
        assert any("Telemetry ingested" in msg for msg in log_messages)
        assert any("msg-12345" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_ingest_telemetry_invalid_payload_raises_400(self) -> None:
        """Test invalid payload raises HTTPException with 400 status."""
        mock_service = MagicMock()
        mock_service.ingest_telemetry = AsyncMock(
            side_effect=InvalidPayloadError("Invalid device_id")
        )

        request = IngestRequest(
            device_id="",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(HTTPException) as exc_info:
            await ingest_telemetry(request, service=mock_service)

        assert exc_info.value.status_code == 400
        assert "Invalid device_id" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_ingest_telemetry_invalid_payload_logs_warning(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test invalid payload logs warning message."""
        import logging

        mock_service = MagicMock()
        mock_service.ingest_telemetry = AsyncMock(
            side_effect=InvalidPayloadError("Invalid timestamp")
        )

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with caplog.at_level(logging.WARNING):
            with pytest.raises(HTTPException):
                await ingest_telemetry(request, service=mock_service)

        log_messages = [record.message for record in caplog.records]
        assert any("Invalid telemetry payload" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_ingest_telemetry_stream_error_raises_503(self) -> None:
        """Test stream publish error raises HTTPException with 503 status."""
        mock_service = MagicMock()
        mock_service.ingest_telemetry = AsyncMock(
            side_effect=StreamPublishError("Redis connection failed")
        )

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(HTTPException) as exc_info:
            await ingest_telemetry(request, service=mock_service)

        assert exc_info.value.status_code == 503
        assert "Service temporarily unavailable" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_ingest_telemetry_stream_error_logs_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test stream error logs error message."""
        import logging

        mock_service = MagicMock()
        mock_service.ingest_telemetry = AsyncMock(
            side_effect=StreamPublishError("Connection timeout")
        )

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with caplog.at_level(logging.ERROR):
            with pytest.raises(HTTPException):
                await ingest_telemetry(request, service=mock_service)

        log_messages = [record.message for record in caplog.records]
        assert any("Failed to publish telemetry" in msg for msg in log_messages)


class TestHealthCheck:
    """Test health_check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self) -> None:
        """Test health check returns healthy status."""
        mock_service = MagicMock()
        mock_service.check_health = AsyncMock(return_value=True)
        mock_service.get_uptime_seconds = MagicMock(return_value=3600.5)

        response = await health_check(service=mock_service)

        assert response.status == "healthy"
        assert response.redis_connected is True
        assert response.uptime_seconds == 3600.5

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self) -> None:
        """Test health check returns unhealthy status."""
        mock_service = MagicMock()
        mock_service.check_health = AsyncMock(return_value=False)
        mock_service.get_uptime_seconds = MagicMock(return_value=120.0)

        response = await health_check(service=mock_service)

        assert response.status == "unhealthy"
        assert response.redis_connected is False
        assert response.uptime_seconds == 120.0

    @pytest.mark.asyncio
    async def test_health_check_calls_service_methods(self) -> None:
        """Test health check calls service check_health and get_uptime_seconds."""
        mock_service = MagicMock()
        mock_service.check_health = AsyncMock(return_value=True)
        mock_service.get_uptime_seconds = MagicMock(return_value=7200.0)

        await health_check(service=mock_service)

        mock_service.check_health.assert_called_once()
        mock_service.get_uptime_seconds.assert_called_once()


__all__ = ["TestHealthCheck", "TestIngestTelemetry"]
