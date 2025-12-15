"""Additional tests for TelemetryWorker edge cases."""

import pytest

from src.processor.worker import TelemetryWorker
from unittest.mock import AsyncMock, MagicMock


class TestTelemetryWorkerEdgeCases:
    """Test TelemetryWorker edge cases and validation."""

    def test_worker_validates_consumer_not_none(self) -> None:
        """Test worker raises ValueError if consumer is None."""
        with pytest.raises(ValueError, match="consumer cannot be None"):
            TelemetryWorker(
                consumer=None,
                aggregator=AsyncMock(),
                detector=MagicMock(),
                storage=AsyncMock(),
                alerter=AsyncMock(),
            )

    def test_worker_validates_aggregator_not_none(self) -> None:
        """Test worker raises ValueError if aggregator is None."""
        with pytest.raises(ValueError, match="aggregator cannot be None"):
            TelemetryWorker(
                consumer=AsyncMock(),
                aggregator=None,
                detector=MagicMock(),
                storage=AsyncMock(),
                alerter=AsyncMock(),
            )

    def test_worker_validates_detector_not_none(self) -> None:
        """Test worker raises ValueError if detector is None."""
        with pytest.raises(ValueError, match="detector cannot be None"):
            TelemetryWorker(
                consumer=AsyncMock(),
                aggregator=AsyncMock(),
                detector=None,
                storage=AsyncMock(),
                alerter=AsyncMock(),
            )

    def test_worker_validates_storage_not_none(self) -> None:
        """Test worker raises ValueError if storage is None."""
        with pytest.raises(ValueError, match="storage cannot be None"):
            TelemetryWorker(
                consumer=AsyncMock(),
                aggregator=AsyncMock(),
                detector=MagicMock(),
                storage=None,
                alerter=AsyncMock(),
            )

    def test_worker_validates_alerter_not_none(self) -> None:
        """Test worker raises ValueError if alerter is None."""
        with pytest.raises(ValueError, match="alerter cannot be None"):
            TelemetryWorker(
                consumer=AsyncMock(),
                aggregator=AsyncMock(),
                detector=MagicMock(),
                storage=AsyncMock(),
                alerter=None,
            )

    async def test_stop_when_not_running(self) -> None:
        """Test stop logs warning when worker not running."""
        worker = TelemetryWorker(
            consumer=AsyncMock(),
            aggregator=AsyncMock(),
            detector=MagicMock(),
            storage=AsyncMock(),
            alerter=AsyncMock(),
        )
        
        # Stop without starting
        await worker.stop()
        
        # Should complete without error
        assert worker._running is False


__all__: list[str] = []
