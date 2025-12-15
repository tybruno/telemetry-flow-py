"""Tests for FastAPI dependency injection."""

import logging
from unittest.mock import MagicMock

import pytest

from src.ingest import dependencies
from src.ingest.service import IngestService
from src.streams.partitioner import StreamPartitioner


class TestGetStream:
    """Test get_stream dependency."""

    def test_get_stream_returns_stream_when_initialized(self) -> None:
        """Test get_stream returns stream when initialized."""
        mock_stream = MagicMock()
        mock_partitioner = StreamPartitioner(num_partitions=3)

        # Initialize service to set global instances
        dependencies.initialize_service(
            stream=mock_stream, partitioner=mock_partitioner
        )

        retrieved_stream = dependencies.get_stream()

        assert retrieved_stream is mock_stream

    def test_get_stream_raises_when_not_initialized(self) -> None:
        """Test get_stream raises RuntimeError when not initialized."""
        # Reset global state
        dependencies._stream_instance = None

        with pytest.raises(RuntimeError) as exc_info:
            dependencies.get_stream()

        assert "Stream not initialized" in str(exc_info.value)

    def test_get_stream_not_initialized_logs_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test get_stream logs error when not initialized."""
        # Reset global state
        dependencies._stream_instance = None

        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError):
                dependencies.get_stream()

        log_messages = [record.message for record in caplog.records]
        assert any(
            "Stream not initialized" in msg and "initialize_service" in msg
            for msg in log_messages
        )


class TestGetIngestService:
    """Test get_ingest_service dependency."""

    def test_get_ingest_service_returns_service_when_initialized(self) -> None:
        """Test get_ingest_service returns service when initialized."""
        mock_stream = MagicMock()
        mock_partitioner = StreamPartitioner(num_partitions=3)

        # Initialize service to set global instances
        dependencies.initialize_service(
            stream=mock_stream, partitioner=mock_partitioner
        )

        retrieved_service = dependencies.get_ingest_service()

        assert isinstance(retrieved_service, IngestService)
        assert retrieved_service is dependencies._service_instance

    def test_get_ingest_service_raises_when_not_initialized(self) -> None:
        """Test get_ingest_service raises RuntimeError when not initialized."""
        # Reset global state
        dependencies._service_instance = None

        with pytest.raises(RuntimeError) as exc_info:
            dependencies.get_ingest_service()

        assert "Service not initialized" in str(exc_info.value)

    def test_get_ingest_service_not_initialized_logs_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test get_ingest_service logs error when not initialized."""
        # Reset global state
        dependencies._service_instance = None

        with caplog.at_level(logging.ERROR):
            with pytest.raises(RuntimeError):
                dependencies.get_ingest_service()

        log_messages = [record.message for record in caplog.records]
        assert any(
            "Service not initialized" in msg and "initialize_service" in msg
            for msg in log_messages
        )


class TestInitializeService:
    """Test initialize_service function."""

    def test_initialize_service_creates_service_instance(self) -> None:
        """Test initialize_service creates IngestService instance."""
        mock_stream = MagicMock()
        mock_partitioner = StreamPartitioner(num_partitions=5)

        dependencies.initialize_service(
            stream=mock_stream, partitioner=mock_partitioner
        )

        assert dependencies._service_instance is not None
        assert isinstance(dependencies._service_instance, IngestService)

    def test_initialize_service_sets_stream_instance(self) -> None:
        """Test initialize_service sets stream instance."""
        mock_stream = MagicMock()
        mock_partitioner = StreamPartitioner(num_partitions=3)

        dependencies.initialize_service(
            stream=mock_stream, partitioner=mock_partitioner
        )

        assert dependencies._stream_instance is mock_stream

    def test_initialize_service_sets_partitioner_instance(self) -> None:
        """Test initialize_service sets partitioner instance."""
        mock_stream = MagicMock()
        mock_partitioner = StreamPartitioner(num_partitions=4)

        dependencies.initialize_service(
            stream=mock_stream, partitioner=mock_partitioner
        )

        assert dependencies._partitioner_instance is mock_partitioner

    def test_initialize_service_logs_info(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test initialize_service logs initialization info."""
        mock_stream = MagicMock()
        mock_partitioner = StreamPartitioner(num_partitions=7)

        with caplog.at_level(logging.INFO):
            dependencies.initialize_service(
                stream=mock_stream, partitioner=mock_partitioner
            )

        log_messages = [record.message for record in caplog.records]
        assert any("Ingest service initialized" in msg for msg in log_messages)
        assert any("7 partitions" in msg for msg in log_messages)

    def test_initialize_service_can_be_called_multiple_times(self) -> None:
        """Test initialize_service can be called multiple times (re-initialization)."""
        mock_stream_1 = MagicMock()
        mock_partitioner_1 = StreamPartitioner(num_partitions=3)

        dependencies.initialize_service(
            stream=mock_stream_1, partitioner=mock_partitioner_1
        )
        service_1 = dependencies._service_instance

        mock_stream_2 = MagicMock()
        mock_partitioner_2 = StreamPartitioner(num_partitions=5)

        dependencies.initialize_service(
            stream=mock_stream_2, partitioner=mock_partitioner_2
        )
        service_2 = dependencies._service_instance

        # Should create new instance
        assert service_2 is not service_1
        assert dependencies._stream_instance is mock_stream_2


__all__ = ["TestGetIngestService", "TestGetStream", "TestInitializeService"]
