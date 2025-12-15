"""Tests for Ingest Service implementation."""

import logging
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.ingest.exceptions import InvalidPayloadError, StreamPublishError
from src.ingest.models import IngestRequest
from src.ingest.service import IngestService
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
            timestamp=datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
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
            timestamp=datetime.now(timezone.utc),
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
            timestamp=datetime.now(timezone.utc),
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
            timestamp=datetime.now(timezone.utc),
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
            timestamp=datetime(2025, 1, 15, 10, 30, 0),  # No timezone
        )

        with pytest.raises(InvalidPayloadError):
            await service.ingest_telemetry(request)


class TestIngestServiceHealth:
    """Tests for health check."""

    @pytest.mark.asyncio
    async def test_check_health_returns_true_when_stream_available(self) -> None:
        """Test health check returns True when stream is available."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        is_healthy = await service.check_health()

        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_check_health_returns_false_when_stream_none(self) -> None:
        """Test health check returns False when stream is None."""
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=AsyncMock(), partitioner=partitioner)

        # Override stream to None
        service._stream = None

        is_healthy = await service.check_health()

        assert is_healthy is False

    def test_get_uptime_seconds_returns_positive_value(self) -> None:
        """Test get_uptime_seconds returns positive value."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        uptime = service.get_uptime_seconds()

        assert isinstance(uptime, float)
        assert uptime >= 0.0

    def test_get_uptime_seconds_increases_over_time(self) -> None:
        """Test get_uptime_seconds increases over time."""
        import time

        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        uptime_1 = service.get_uptime_seconds()
        time.sleep(0.1)  # Sleep for 100ms
        uptime_2 = service.get_uptime_seconds()

        assert uptime_2 > uptime_1


class TestIngestServiceValidation:
    """Tests for request validation methods."""

    @pytest.mark.asyncio
    async def test_ingest_with_infinite_metric_value_raises(self) -> None:
        """Test validation error for infinite metric value."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=float("inf"),
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(InvalidPayloadError) as exc_info:
            await service.ingest_telemetry(request)

        assert "metric_value must be finite" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_ingest_with_nan_metric_value_raises(self) -> None:
        """Test validation error for NaN metric value."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=float("nan"),
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(InvalidPayloadError) as exc_info:
            await service.ingest_telemetry(request)

        assert "metric_value must be finite" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_ingest_with_multiple_validation_errors(self) -> None:
        """Test validation error message includes all errors."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="",
            interface="",
            metric_name="",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(InvalidPayloadError) as exc_info:
            await service.ingest_telemetry(request)

        error_message = str(exc_info.value)
        assert "device_id cannot be empty" in error_message
        assert "interface cannot be empty" in error_message
        assert "metric_name cannot be empty" in error_message

    @pytest.mark.asyncio
    async def test_validation_error_logs_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test validation error logs error message."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with caplog.at_level(logging.ERROR):
            with pytest.raises(InvalidPayloadError):
                await service.ingest_telemetry(request)

        log_messages = [record.message for record in caplog.records]
        assert any("Validation failed" in msg for msg in log_messages)


class TestIngestServicePublishing:
    """Tests for event publishing."""

    @pytest.mark.asyncio
    async def test_publish_event_uses_partitioned_stream_name(self) -> None:
        """Test publish uses partitioned stream name based on device_id."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-123")
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        )

        await service.ingest_telemetry(request)

        # Verify publish was called with partitioned stream name
        stream.publish.assert_called_once()
        call_kwargs = stream.publish.call_args[1]
        assert "stream" in call_kwargs
        # Stream name should be telemetry:0, telemetry:1, or telemetry:2
        stream_name = call_kwargs["stream"]
        assert stream_name.startswith("telemetry:")
        assert stream_name in ["telemetry:0", "telemetry:1", "telemetry:2"]

    @pytest.mark.asyncio
    async def test_publish_event_serializes_data_correctly(self) -> None:
        """Test event data is serialized correctly for stream."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-456")
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        timestamp = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        request = IngestRequest(
            device_id="router-02",
            interface="eth1",
            metric_name="latency",
            metric_value=12.5,
            timestamp=timestamp,
        )

        await service.ingest_telemetry(request)

        # Verify serialized data
        stream.publish.assert_called_once()
        call_kwargs = stream.publish.call_args[1]
        published_data = call_kwargs["data"]

        assert published_data["device_id"] == "router-02"
        assert published_data["interface"] == "eth1"
        assert published_data["metric_name"] == "latency"
        assert published_data["metric_value"] == "12.5"
        assert published_data["timestamp"] == timestamp.isoformat()

    @pytest.mark.asyncio
    async def test_publish_event_failure_raises_stream_publish_error(self) -> None:
        """Test publish failure raises StreamPublishError."""
        stream = AsyncMock()
        stream.publish = AsyncMock(side_effect=Exception("Redis connection failed"))
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(StreamPublishError) as exc_info:
            await service.ingest_telemetry(request)

        assert "Failed to publish event" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_publish_event_failure_logs_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test publish failure logs error message."""
        stream = AsyncMock()
        stream.publish = AsyncMock(side_effect=Exception("Connection timeout"))
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-01",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with caplog.at_level(logging.ERROR):
            with pytest.raises(StreamPublishError):
                await service.ingest_telemetry(request)

        log_messages = [record.message for record in caplog.records]
        assert any("Failed to publish event" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_publish_event_success_logs_info(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test successful publish logs info message."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-789")
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-03",
            interface="eth0",
            metric_name="bandwidth",
            metric_value=85.5,
            timestamp=datetime.now(timezone.utc),
        )

        with caplog.at_level(logging.INFO):
            await service.ingest_telemetry(request)

        log_messages = [record.message for record in caplog.records]
        assert any("Published telemetry event" in msg for msg in log_messages)
        assert any("msg-789" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_ingest_logs_debug_message(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test ingest_telemetry logs debug message."""
        stream = AsyncMock()
        stream.publish = AsyncMock(return_value="msg-999")
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        request = IngestRequest(
            device_id="router-debug",
            interface="eth5",
            metric_name="throughput",
            metric_value=100.0,
            timestamp=datetime.now(timezone.utc),
        )

        with caplog.at_level(logging.DEBUG):
            await service.ingest_telemetry(request)

        log_messages = [record.message for record in caplog.records]
        assert any("Ingesting telemetry" in msg for msg in log_messages)
        assert any("router-debug" in msg for msg in log_messages)


class TestIngestServiceInitialization:
    """Tests for service initialization."""

    def test_service_initializes_with_default_stream_name(self) -> None:
        """Test service initializes with default base stream name."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        assert service._base_stream_name == "telemetry"

    def test_service_initializes_with_custom_stream_name(self) -> None:
        """Test service initializes with custom base stream name."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(
            stream=stream, partitioner=partitioner, base_stream_name="custom_stream"
        )

        assert service._base_stream_name == "custom_stream"

    def test_service_tracks_start_time(self) -> None:
        """Test service tracks start time for uptime calculation."""
        stream = AsyncMock()
        partitioner = StreamPartitioner(num_partitions=3)
        service = IngestService(stream=stream, partitioner=partitioner)

        assert hasattr(service, "_start_time")
        assert isinstance(service._start_time, datetime)
        assert service._start_time.tzinfo is not None  # Timezone-aware
