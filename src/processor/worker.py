"""Telemetry processor worker orchestration.

This module provides the main processor worker that orchestrates the
complete telemetry processing pipeline: consumption, aggregation,
detection, and alerting.

Classes:
    TelemetryWorker: Main processor worker orchestrating the pipeline.

Example:
    Creating and running a processor worker::

        from processor import TelemetryWorker
        from consumers import TelemetryConsumer
        from aggregation import TumblingWindowAggregator
        from detection import ThresholdDetector

        worker = TelemetryWorker(
            consumer=telemetry_consumer,
            aggregator=TumblingWindowAggregator(window_size=60),
            detector=ThresholdDetector(thresholds={"cpu": 90.0}),
            storage=redis_store,
            alerter=console_alerter
        )

        await worker.start()  # Runs until stopped
"""


from src.aggregation.tumbling_window import TumblingWindowAggregator
from src.consumers.consumer import TelemetryConsumer
from src.core.protocols import AlerterProtocol, StorageProtocol
from src.detection.threshold import ThresholdDetector


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
        "_aggregator",
        "_alerter",
        "_consumer",
        "_detector",
        "_running",
        "_storage",
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
        """Start processing telemetry events.

        Begins consuming events from stream, aggregating metrics,
        detecting anomalies, and sending alerts. Runs until stop()
        is called.

        Raises:
            ConsumerError: If stream consumption fails critically.
            StorageError: If state persistence fails.
            RuntimeError: If worker is already running.

        Example:
            await worker.start()  # Blocks until stopped
        """
        raise NotImplementedError

    async def stop(self) -> None:
        """Stop processing gracefully.

        Signals the worker to stop processing, waits for current
        message to complete, saves state, and closes connections.

        Raises:
            StorageError: If final state save fails.

        Example:
            await worker.stop()  # Graceful shutdown
        """
        raise NotImplementedError


__all__ = ["TelemetryWorker"]
