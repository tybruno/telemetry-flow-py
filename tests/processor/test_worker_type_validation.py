"""Complete tests for TelemetryWorker type validation."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.aggregation.models import WindowBounds, WindowMetrics
from src.core.models import TelemetryEvent
from src.detection.models import AnomalyResult, AnomalySeverity
from src.processor.worker import TelemetryWorker


class TestTelemetryWorkerTypeValidation:
    """Test worker handles invalid types gracefully."""

    @pytest.fixture
    def worker(self) -> TelemetryWorker:
        """Create worker instance.

        Returns:
            TelemetryWorker instance.
        """
        return TelemetryWorker(
            consumer=AsyncMock(),
            aggregator=AsyncMock(),
            detector=MagicMock(),
            storage=AsyncMock(),
            alerter=AsyncMock(),
        )

    def test_log_event_processing_with_telemetry_event(
        self,
        worker: TelemetryWorker,
    ) -> None:
        """Test _log_event_processing with TelemetryEvent.

        Args:
            worker: TelemetryWorker fixture.
        """
        event = TelemetryEvent(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu",
            metric_value=75.0,
            timestamp=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
        )

        # Should not raise
        worker._log_event_processing(event)

    def test_log_event_processing_with_non_event(
        self,
        worker: TelemetryWorker,
    ) -> None:
        """Test _log_event_processing with non-TelemetryEvent.

        Args:
            worker: TelemetryWorker fixture.
        """
        # Should not raise
        worker._log_event_processing({"not": "an event"})

    async def test_detect_and_alert_with_non_window_metrics(
        self,
        worker: TelemetryWorker,
    ) -> None:
        """Test _detect_and_alert returns early for non-WindowMetrics.

        Args:
            worker: TelemetryWorker fixture.
        """
        # Should return early without calling detector
        await worker._detect_and_alert({"not": "metrics"})

        # Detector should not be called
        worker._detector.detect.assert_not_called()

    async def test_send_anomaly_alert_with_invalid_metrics(
        self,
        worker: TelemetryWorker,
    ) -> None:
        """Test _send_anomaly_alert returns early for invalid metrics.

        Args:
            worker: TelemetryWorker fixture.
        """
        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0,
        )
        anomaly = AnomalyResult(
            is_anomaly=True,
            severity=AnomalySeverity.HIGH,
            confidence=0.95,
            description="Test",
            detected_at=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            metric_value=95.0,
            threshold_value=80.0,
        )

        # Should return early
        await worker._send_anomaly_alert({"not": "metrics"}, anomaly)

        # Alerter should not be called
        worker._alerter.send_alert.assert_not_called()

    async def test_send_anomaly_alert_with_invalid_anomaly(
        self,
        worker: TelemetryWorker,
    ) -> None:
        """Test _send_anomaly_alert returns early for invalid anomaly.

        Args:
            worker: TelemetryWorker fixture.
        """
        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0,
        )
        metrics = WindowMetrics(
            window_bounds=bounds,
            average=95.0,
            minimum=90.0,
            maximum=99.0,
            stddev=3.0,
            count=10,
            sum=950.0,
        )

        # Should return early
        await worker._send_anomaly_alert(metrics, {"not": "anomaly"})

        # Alerter should not be called
        worker._alerter.send_alert.assert_not_called()


__all__: list[str] = []
