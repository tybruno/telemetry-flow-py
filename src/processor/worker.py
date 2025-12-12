"""Telemetry processor worker orchestration.

Class:
    TelemetryWorker: Main processor worker orchestrating the pipeline.
"""

import logging as _log

from src.core.protocols import AlerterProtocol, StorageProtocol
from src.processor.aggregator import TumblingWindowAggregator
from src.processor.consumer import TelemetryConsumer
from src.processor.detector import ThresholdDetector


class TelemetryWorker:
    """Main worker for processing telemetry event streams.

    Orchestrates the complete processing pipeline: stream consumption,
    time-windowed aggregation, anomaly detection, and alerting.

    Uses dependency injection for all components enabling testing
    and implementation swapping.

    Attributes:
        _consumer: Consumes and deserializes telemetry events.
        _aggregator: Aggregates metrics in time windows.
        _detector: Detects anomalies via threshold comparison.
        _storage: Persists worker state for recovery.
        _alerter: Sends alerts for detected anomalies.
        _running: Flag indicating active processing state.

    Example:
        worker = TelemetryWorker(
            consumer=consumer,
            aggregator=TumblingWindowAggregator(window_size=60),
            detector=ThresholdDetector(thresholds={...}),
            storage=storage,
            alerter=alerter
        )

        await worker.start()
        # Processes until stopped
        await worker.stop()
    """

    __slots__ = (
        "_consumer",
        "_aggregator",
        "_detector",
        "_storage",
        "_alerter",
        "_running",
    )

    _consumer: TelemetryConsumer
    _aggregator: TumblingWindowAggregator
    _detector: ThresholdDetector
    _storage: StorageProtocol
    _alerter: AlerterProtocol
    _running: bool

    def __init__(
        self,
        *,
        consumer: TelemetryConsumer,
        aggregator: TumblingWindowAggregator,
        detector: ThresholdDetector,
        storage: StorageProtocol,
        alerter: AlerterProtocol,
    ) -> None:
        """Initialize worker with injected dependencies.

        Args:
            consumer: Telemetry event consumer.
            aggregator: Time-window aggregator.
            detector: Anomaly detector.
            storage: State storage.
            alerter: Alert delivery.

        Raises:
            ValueError: If any dependency is None.
        """
        raise NotImplementedError

    async def start(self) -> None:
        """Start processing telemetry events."""
        raise NotImplementedError

    async def stop(self) -> None:
        """Stop processing gracefully."""
        raise NotImplementedError


__all__ = ["TelemetryWorker"]
