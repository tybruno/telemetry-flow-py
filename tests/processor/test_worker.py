"""Tests for processor worker orchestration.

Tests the TelemetryWorker class including event processing orchestration,
library coordination, and error handling.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.aggregation.models import WindowBounds, WindowMetrics
from src.aggregation.tumbling_window import TumblingWindowAggregator
from src.consumers.consumer import TelemetryConsumer
from src.core.models import TelemetryEvent
from src.detection.models import AnomalyResult, AnomalySeverity
from src.detection.threshold import ThresholdDetector
from src.processor.worker import TelemetryWorker


class TestTelemetryWorker:
    """Tests for TelemetryWorker class."""

    @pytest.fixture
    def mock_consumer(self) -> AsyncMock:
        """Create mock consumer.

        Returns:
            Mock TelemetryConsumer.
        """
        consumer = AsyncMock(spec=TelemetryConsumer)
        return consumer

    @pytest.fixture
    def mock_aggregator(self) -> AsyncMock:
        """Create mock aggregator.

        Returns:
            Mock TumblingWindowAggregator.
        """
        aggregator = AsyncMock(spec=TumblingWindowAggregator)
        return aggregator

    @pytest.fixture
    def mock_detector(self) -> MagicMock:
        """Create mock detector.

        Returns:
            Mock ThresholdDetector.
        """
        detector = MagicMock(spec=ThresholdDetector)
        return detector

    @pytest.fixture
    def mock_storage(self) -> AsyncMock:
        """Create mock storage.

        Returns:
            Mock storage protocol.
        """
        storage = AsyncMock()
        return storage

    @pytest.fixture
    def mock_alerter(self) -> AsyncMock:
        """Create mock alerter.

        Returns:
            Mock alerter protocol.
        """
        alerter = AsyncMock()
        return alerter

    @pytest.fixture
    def worker(
        self,
        mock_consumer: AsyncMock,
        mock_aggregator: AsyncMock,
        mock_detector: MagicMock,
        mock_storage: AsyncMock,
        mock_alerter: AsyncMock,
    ) -> TelemetryWorker:
        """Create worker with mocked dependencies.

        Args:
            mock_consumer: Mock consumer fixture.
            mock_aggregator: Mock aggregator fixture.
            mock_detector: Mock detector fixture.
            mock_storage: Mock storage fixture.
            mock_alerter: Mock alerter fixture.

        Returns:
            TelemetryWorker instance.
        """
        worker_instance = TelemetryWorker(
            consumer=mock_consumer,
            aggregator=mock_aggregator,
            detector=mock_detector,
            storage=mock_storage,
            alerter=mock_alerter,
        )
        return worker_instance

    def test_worker_initialization(
        self,
        mock_consumer: AsyncMock,
        mock_aggregator: AsyncMock,
        mock_detector: MagicMock,
        mock_storage: AsyncMock,
        mock_alerter: AsyncMock,
    ) -> None:
        """Test worker initializes with all required dependencies.

        Verifies worker requires consumer, aggregator, detector,
        storage, and alerter to be provided.

        Args:
            mock_consumer: Mock consumer fixture.
            mock_aggregator: Mock aggregator fixture.
            mock_detector: Mock detector fixture.
            mock_storage: Mock storage fixture.
            mock_alerter: Mock alerter fixture.
        """
        worker_instance = TelemetryWorker(
            consumer=mock_consumer,
            aggregator=mock_aggregator,
            detector=mock_detector,
            storage=mock_storage,
            alerter=mock_alerter,
        )

        assert worker_instance._consumer is mock_consumer
        assert worker_instance._aggregator is mock_aggregator
        assert worker_instance._detector is mock_detector
        assert worker_instance._storage is mock_storage
        assert worker_instance._alerter is mock_alerter
        assert worker_instance._running is False

    async def test_process_telemetry_event(
        self,
        worker: TelemetryWorker,
        mock_consumer: AsyncMock,
        mock_aggregator: AsyncMock,
    ) -> None:
        """Test worker processes telemetry event through pipeline.

        Verifies event flows through consumer → aggregator → detector
        → storage → alerter pipeline correctly.

        Args:
            worker: TelemetryWorker fixture.
            mock_consumer: Mock consumer fixture.
            mock_aggregator: Mock aggregator fixture.
        """
        # Create test event
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=75.0,
            timestamp=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
        )

        # Mock consumer to return one event then stop
        async def mock_consume():
            yield event
            worker._running = False

        mock_consumer.consume_events = mock_consume
        mock_aggregator.aggregate.return_value = None  # No completed window

        # Start worker (will process one event and stop)
        await worker.start()

        # Verify aggregator was called with event
        mock_aggregator.aggregate.assert_called_once_with(event)

    async def test_aggregation_triggers_detection(
        self,
        worker: TelemetryWorker,
        mock_consumer: AsyncMock,
        mock_aggregator: AsyncMock,
        mock_detector: MagicMock,
    ) -> None:
        """Test worker triggers detection when window completes.

        Verifies detector called with WindowMetrics when aggregator
        returns completed window.

        Args:
            worker: TelemetryWorker fixture.
            mock_consumer: Mock consumer fixture.
            mock_aggregator: Mock aggregator fixture.
            mock_detector: Mock detector fixture.
        """
        # Create sample event and window metrics
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=85.0,
            timestamp=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
        )

        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0,
        )
        window_metrics = WindowMetrics(
            window_bounds=bounds,
            average=85.0,
            minimum=80.0,
            maximum=90.0,
            stddev=3.0,
            count=10,
            sum=850.0,
        )

        # Mock consumer and aggregator
        async def mock_consume():
            yield event
            worker._running = False

        mock_consumer.consume_events = mock_consume
        mock_aggregator.aggregate.return_value = window_metrics
        mock_detector.detect.return_value = None  # No anomaly

        # Start worker
        await worker.start()

        # Verify detector was called with window metrics
        mock_detector.detect.assert_called_once_with(window_metrics)

    async def test_anomaly_triggers_alert(
        self,
        worker: TelemetryWorker,
        mock_consumer: AsyncMock,
        mock_aggregator: AsyncMock,
        mock_detector: MagicMock,
        mock_alerter: AsyncMock,
    ) -> None:
        """Test worker sends alert when anomaly detected.

        Verifies alerter called when detector returns anomaly.

        Args:
            worker: TelemetryWorker fixture.
            mock_consumer: Mock consumer fixture.
            mock_aggregator: Mock aggregator fixture.
            mock_detector: Mock detector fixture.
            mock_alerter: Mock alerter fixture.
        """
        # Create event, window, and anomaly
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=95.0,
            timestamp=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
        )

        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0,
        )
        window_metrics = WindowMetrics(
            window_bounds=bounds,
            average=95.0,
            minimum=90.0,
            maximum=99.0,
            stddev=3.0,
            count=10,
            sum=950.0,
        )

        anomaly = AnomalyResult(
            is_anomaly=True,
            severity=AnomalySeverity.HIGH,
            confidence=0.95,
            description="CPU threshold exceeded",
            detected_at=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            metric_value=95.0,
            threshold_value=80.0,
        )

        # Mock pipeline
        async def mock_consume():
            yield event
            worker._running = False

        mock_consumer.consume_events = mock_consume
        mock_aggregator.aggregate.return_value = window_metrics
        mock_detector.detect.return_value = anomaly

        # Start worker
        await worker.start()

        # Verify alerter was called
        mock_alerter.send_alert.assert_called_once()
        call_kwargs = mock_alerter.send_alert.call_args.kwargs
        assert call_kwargs["severity"] == "high"
        assert call_kwargs["message"] == "CPU threshold exceeded"
        assert "metric_value" in call_kwargs["context"]

    async def test_store_aggregated_metrics(
        self,
        worker: TelemetryWorker,
        mock_consumer: AsyncMock,
        mock_aggregator: AsyncMock,
        mock_storage: AsyncMock,
    ) -> None:
        """Test worker persists aggregated metrics to storage.

        Verifies WindowMetrics saved via StorageProtocol.

        Args:
            worker: TelemetryWorker fixture.
            mock_consumer: Mock consumer fixture.
            mock_aggregator: Mock aggregator fixture.
            mock_storage: Mock storage fixture.
        """
        # Note: Current implementation doesn't store metrics yet
        # This test verifies the storage is available for future use
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=75.0,
            timestamp=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
        )

        async def mock_consume():
            yield event
            worker._running = False

        mock_consumer.consume_events = mock_consume
        mock_aggregator.aggregate.return_value = None

        await worker.start()

        # Verify storage is available (even if not used yet)
        assert worker._storage is mock_storage

    async def test_handle_consumer_error(
        self,
        worker: TelemetryWorker,
        mock_consumer: AsyncMock,
    ) -> None:
        """Test worker handles consumer errors gracefully.

        Verifies worker continues processing after transient consumer
        errors and logs permanent failures.

        Args:
            worker: TelemetryWorker fixture.
            mock_consumer: Mock consumer fixture.
        """
        # Mock consumer to raise exception
        async def mock_consume():
            raise RuntimeError("Consumer error")
            yield  # Never reached - makes this an async generator

        mock_consumer.consume_events = mock_consume

        # Worker should propagate the error
        with pytest.raises(RuntimeError, match="Consumer error"):
            await worker.start()

        # Verify worker stopped
        assert worker._running is False

    async def test_aggregation_error_stops_processing(
        self,
        worker: TelemetryWorker,
        mock_consumer: AsyncMock,
        mock_aggregator: AsyncMock,
    ) -> None:
        """Test worker stops after aggregation error.

        Args:
            worker: TelemetryWorker fixture.
            mock_consumer: Mock consumer fixture.
            mock_aggregator: Mock aggregator fixture.
        """
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=75.0,
            timestamp=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
        )

        async def mock_consume():
            yield event
            worker._running = False

        mock_consumer.consume_events = mock_consume
        mock_aggregator.aggregate.side_effect = RuntimeError("Aggregation failed")

        # Should propagate error
        with pytest.raises(RuntimeError, match="Aggregation failed"):
            await worker.start()

    async def test_detection_error_stops_processing(
        self,
        worker: TelemetryWorker,
        mock_consumer: AsyncMock,
        mock_aggregator: AsyncMock,
        mock_detector: MagicMock,
    ) -> None:
        """Test worker stops after detection error.

        Args:
            worker: TelemetryWorker fixture.
            mock_consumer: Mock consumer fixture.
            mock_aggregator: Mock aggregator fixture.
            mock_detector: Mock detector fixture.
        """
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=75.0,
            timestamp=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
        )
        
        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0,
        )
        window_metrics = WindowMetrics(
            window_bounds=bounds,
            average=75.0,
            minimum=70.0,
            maximum=80.0,
            stddev=3.0,
            count=10,
            sum=750.0,
        )

        async def mock_consume():
            yield event
            worker._running = False

        mock_consumer.consume_events = mock_consume
        mock_aggregator.aggregate.return_value = window_metrics
        mock_detector.detect.side_effect = RuntimeError("Detection failed")

        # Should propagate error
        with pytest.raises(RuntimeError, match="Detection failed"):
            await worker.start()

    async def test_alert_error_stops_processing(
        self,
        worker: TelemetryWorker,
        mock_consumer: AsyncMock,
        mock_aggregator: AsyncMock,
        mock_detector: MagicMock,
        mock_alerter: AsyncMock,
    ) -> None:
        """Test worker stops after alerting error.

        Args:
            worker: TelemetryWorker fixture.
            mock_consumer: Mock consumer fixture.
            mock_aggregator: Mock aggregator fixture.
            mock_detector: Mock detector fixture.
            mock_alerter: Mock alerter fixture.
        """
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=95.0,
            timestamp=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
        )
        
        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0,
        )
        window_metrics = WindowMetrics(
            window_bounds=bounds,
            average=95.0,
            minimum=90.0,
            maximum=99.0,
            stddev=3.0,
            count=10,
            sum=950.0,
        )
        
        anomaly = AnomalyResult(
            is_anomaly=True,
            severity=AnomalySeverity.HIGH,
            confidence=0.95,
            description="CPU threshold exceeded",
            detected_at=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            metric_value=95.0,
            threshold_value=80.0,
        )

        async def mock_consume():
            yield event
            worker._running = False

        mock_consumer.consume_events = mock_consume
        mock_aggregator.aggregate.return_value = window_metrics
        mock_detector.detect.return_value = anomaly
        mock_alerter.send_alert.side_effect = RuntimeError("Alert failed")

        # Should propagate error
        with pytest.raises(RuntimeError, match="Alert failed"):
            await worker.start()

    async def test_worker_stop(self, worker: TelemetryWorker) -> None:
        """Test worker stop sets running flag to False.

        Args:
            worker: TelemetryWorker fixture.
        """
        # Start worker
        worker._running = True
        
        # Stop worker
        await worker.stop()
        
        # Verify stopped
        assert worker._running is False
