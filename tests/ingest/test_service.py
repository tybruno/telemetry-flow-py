"""Tests for Ingest Service implementation."""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone

from src.ingest.service import IngestService
from src.ingest.models import IngestRequest
from src.ingest.exceptions import InvalidPayloadError
from src.streams.partitioner import StreamPartitioner


class TestIngestServiceIngest:
    """Tests for ingest_telemetry method."""

    @pytest.mark.asyncio
    async def test_ingest_valid_request(self) -> None:
        """Test ingesting valid request."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-123")
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        )

        response = await service.ingest_telemetry(request)

        assert response.status == "accepted"
        assert response.event_id == "msg-123"

    @pytest.mark.asyncio
    async def test_ingest_with_empty_device_id_raises(self) -> None:
        """Test validation error for empty device_id."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc)
        )

        with pytest.raises(InvalidPayloadError):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_empty_interface_raises(self) -> None:
        """Test validation error for empty interface."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc)
        )

        with pytest.raises(InvalidPayloadError):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_empty_metric_name_raises(self) -> None:
        """Test validation error for empty metric_name."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc)
        )

        with pytest.raises(InvalidPayloadError):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_naive_timestamp_raises(self) -> None:
        """Test validation error for naive timestamp."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime(2025, 1, 15, 10, 30, 0)  # No timezone
        )

        with pytest.raises(InvalidPayloadError):
            await service.ingest_telemetry(request)


class TestIngestServiceHealth:
    """Tests for health check."""

    @pytest.mark.asyncio
    async def test_check_health(self) -> None:
        """Test health check."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        is_healthy = await service.check_health()

        assert isinstance(is_healthy, bool)
