"""Tests for Ingest Service implementation.

Tests the IngestService class including request validation, transformation,
publishing, and health checks.
"""

import math
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta

from src.ingest.service import IngestService
from src.ingest.models import IngestRequest, IngestResponse
from src.ingest.exceptions import InvalidPayloadError, StreamPublishError
from src.streams.partitioner import StreamPartitioner


class TestIngestServiceInitialization:
    """Tests for IngestService initialization."""

    def test_init_with_default_stream_name(self) -> None:
        """Test initialization with default stream name."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        
        service = IngestService(stream=stream, partitioner=partitioner)
        
        assert service._stream is stream
        assert service._partitioner is partitioner
        assert service._base_stream_name == "telemetry"
        assert service._start_time is not None

    def test_init_with_custom_stream_name(self) -> None:
        """Test initialization with custom stream name."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=5)
        
        service = IngestService(
            stream=stream,
            partitioner=partitioner,
            base_stream_name="metrics"
        )
        
        assert service._base_stream_name == "metrics"
        assert service._partitioner.num_partitions == 5


class TestIngestServiceIngestTelemetry:
    """Tests for ingest_telemetry method."""

    @pytest.mark.asyncio
    async def test_ingest_valid_request(self) -> None:
        """Test ingesting valid telemetry request."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-12345")
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
        assert response.event_id == "msg-12345"
        assert response.device_id == "router-01"
        stream.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_ingest_uses_correct_partition(self) -> None:
        """Test that ingestion uses correct partition for device."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-abc")
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=75.0,
            timestamp=datetime.now(timezone.utc)
        )

        await service.ingest_telemetry(request)

        # Check that publish was called with partitioned stream name
        call_args = stream.publish.call_args
        stream_name = call_args[1]["stream"]
        expected_partition = partitioner.get_partition("router-01")
        assert stream_name == f"telemetry-{expected_partition}"

    @pytest.mark.asyncio
    async def test_ingest_with_empty_device_id_raises(self) -> None:
        """Test ingesting with empty device_id raises InvalidPayloadError."""
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

        with pytest.raises(InvalidPayloadError, match="device_id cannot be empty"):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_empty_interface_raises(self) -> None:
        """Test ingesting with empty interface raises InvalidPayloadError."""
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

        with pytest.raises(InvalidPayloadError, match="interface cannot be empty"):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_empty_metric_name_raises(self) -> None:
        """Test ingesting with empty metric_name raises InvalidPayloadError."""
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

        with pytest.raises(InvalidPayloadError, match="metric_name cannot be empty"):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_negative_metric_value_raises(self) -> None:
        """Test ingesting with negative metric_value raises InvalidPayloadError."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=-10.5,
            timestamp=datetime.now(timezone.utc)
        )

        with pytest.raises(InvalidPayloadError, match="metric_value cannot be negative"):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_nan_metric_value_raises(self) -> None:
        """Test ingesting with NaN metric_value raises InvalidPayloadError."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=math.nan,
            timestamp=datetime.now(timezone.utc)
        )

        with pytest.raises(InvalidPayloadError, match="metric_value cannot be NaN"):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_infinite_metric_value_raises(self) -> None:
        """Test ingesting with infinite metric_value raises InvalidPayloadError."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=math.inf,
            timestamp=datetime.now(timezone.utc)
        )

        with pytest.raises(InvalidPayloadError, match="metric_value cannot be infinite"):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_future_timestamp_raises(self) -> None:
        """Test ingesting with future timestamp raises InvalidPayloadError."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        future_time = datetime.now(timezone.utc) + timedelta(hours=2)
        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=future_time
        )

        with pytest.raises(InvalidPayloadError, match="timestamp cannot be in the future"):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_naive_timestamp_raises(self) -> None:
        """Test ingesting with naive (no timezone) timestamp raises."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        naive_timestamp = datetime(2025, 1, 15, 10, 30, 0)  # No timezone
        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=naive_timestamp
        )

        with pytest.raises(InvalidPayloadError, match="timestamp must have timezone"):
            await service.ingest_telemetry(request)

    @pytest.mark.asyncio
    async def test_ingest_with_multiple_validation_errors_raises(self) -> None:
        """Test ingesting with multiple validation errors reports all."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="",  # Invalid
            interface="eth0",
            metric_name="",  # Invalid
            metric_value=-5.0,  # Invalid
            timestamp=datetime.now(timezone.utc)
        )

        with pytest.raises(InvalidPayloadError) as exc_info:
            await service.ingest_telemetry(request)

        error_message = str(exc_info.value)
        assert "device_id" in error_message
        assert "metric_name" in error_message
        assert "metric_value" in error_message

    @pytest.mark.asyncio
    async def test_ingest_publish_error_raises(self) -> None:
        """Test ingesting when publish fails raises StreamPublishError."""
        stream = AsyncMock()
        stream.publish = AsyncMock(side_effect=Exception("Redis connection lost"))
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc)
        )

        with pytest.raises(StreamPublishError, match="Failed to publish event"):
            await service.ingest_telemetry(request)


class TestIngestServiceHealthCheck:
    """Tests for check_health method."""

    @pytest.mark.asyncio
    async def test_check_health_success(self) -> None:
        """Test health check returns True when healthy."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        is_healthy = await service.check_health()

        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_check_health_with_stream_error(self) -> None:
        """Test health check returns False on stream error."""
        stream = None  # Simulate missing stream
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        is_healthy = await service.check_health()

        assert is_healthy is False


class TestIngestServiceUptime:
    """Tests for get_uptime_seconds method."""

    def test_get_uptime_initially(self) -> None:
        """Test uptime is near zero initially."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        uptime = service.get_uptime_seconds()

        assert uptime >= 0
        assert uptime < 1.0  # Should be less than 1 second

    def test_get_uptime_increases(self) -> None:
        """Test uptime increases over time."""
        import time
        
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        uptime1 = service.get_uptime_seconds()
        time.sleep(0.1)
        uptime2 = service.get_uptime_seconds()

        assert uptime2 > uptime1


class TestIngestServiceEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_ingest_with_very_large_metric_value(self) -> None:
        """Test ingesting with very large but valid metric value."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-large")
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=999999999.99,
            timestamp=datetime.now(timezone.utc)
        )

        response = await service.ingest_telemetry(request)

        assert response.status == "accepted"

    @pytest.mark.asyncio
    async def test_ingest_with_zero_metric_value(self) -> None:
        """Test ingesting with zero metric value is valid."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-zero")
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=0.0,
            timestamp=datetime.now(timezone.utc)
        )

        response = await service.ingest_telemetry(request)

        assert response.status == "accepted"

    @pytest.mark.asyncio
    async def test_ingest_with_special_characters_in_device_id(self) -> None:
        """Test ingesting with special characters in device_id."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-special")
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01-prod_v2",
            interface="eth0/1",
            metric_name="cpu_usage",
            metric_value=75.0,
            timestamp=datetime.now(timezone.utc)
        )

        response = await service.ingest_telemetry(request)

        assert response.status == "accepted"
