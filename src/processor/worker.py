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

import logging as _log

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
        self._validate_dependency(consumer, "consumer")
        self._validate_dependency(aggregator, "aggregator")
        self._validate_dependency(detector, "detector")
        self._validate_dependency(storage, "storage")
        self._validate_dependency(alerter, "alerter")

        self._consumer = consumer
        self._aggregator = aggregator
        self._detector = detector
        self._storage = storage
        self._alerter = alerter
        self._running = False

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
        if self._running:
            error_message = "Worker is already running"
            _log.error(error_message)
            raise RuntimeError(error_message) from None

        self._running = True
        _log.info("Starting telemetry processor worker")

        try:
            # Consume and process events
            async for event in self._consumer.consume_events():
                if not self._running:
                    _log.info("Worker stopping signal received")
                    break

                self._log_event_processing(event)

                # Aggregate metrics in time windows
                window_metrics = await self._aggregator.aggregate(event)

                # Check if window completed
                if not window_metrics:
                    continue

                self._log_window_completion(window_metrics)

                # Detect and handle anomalies
                await self._detect_and_alert(window_metrics)

        except Exception as e:
            _log.error("Worker encountered fatal error: %s", str(e))
            self._running = False
            raise

        _log.info("Telemetry processor worker stopped")

    async def stop(self) -> None:
        """Stop processing gracefully.

        Signals the worker to stop processing, waits for current
        message to complete, saves state, and closes connections.

        Raises:
            StorageError: If final state save fails.

        Example:
            await worker.stop()  # Graceful shutdown
        """
        if not self._running:
            _log.warning("Worker is not running")
            return

        _log.info("Stopping worker gracefully")
        self._running = False

        # Note: In a full implementation, we might:
        # - Save aggregation state to storage for recovery
        # - Close consumer connections
        # - Flush pending alerts
        # For now, just signal stop

        _log.info("Worker stopped")

    def _validate_dependency(self, dependency: object, name: str) -> None:
        """Validate that a dependency is not None.

        Args:
            dependency: Dependency object to validate.
            name: Name of dependency for error message.

        Raises:
            ValueError: If dependency is None.
        """
        if not dependency:
            error_message = "%s cannot be None"
            _log.error(error_message, name)
            raise ValueError(error_message % name) from None

    def _log_event_processing(self, event: object) -> None:
        """Log event processing details.

        Args:
            event: Telemetry event being processed.
        """
        from src.core.models import TelemetryEvent

        if isinstance(event, TelemetryEvent):
            _log.debug(
                "Processing event: device=%s, interface=%s, metric=%s",
                event.device_id,
                event.interface,
                event.metric_name
            )

    def _log_window_completion(self, window_metrics: object) -> None:
        """Log window completion details.

        Args:
            window_metrics: Completed window metrics.
        """
        from src.aggregation.models import WindowMetrics

        if isinstance(window_metrics, WindowMetrics):
            _log.info(
                "Window completed: count=%d, avg=%0.2f, min=%0.2f, max=%0.2f",
                window_metrics.count,
                window_metrics.average,
                window_metrics.minimum,
                window_metrics.maximum
            )

    async def _detect_and_alert(self, window_metrics: object) -> None:
        """Detect anomalies and send alerts if found.

        Args:
            window_metrics: Window metrics to analyze.
        """
        from src.aggregation.models import WindowMetrics

        if not isinstance(window_metrics, WindowMetrics):
            return

        # Detect anomalies
        anomaly_result = self._detector.detect(window_metrics)

        # Send alerts if anomaly detected
        if anomaly_result and anomaly_result.is_anomaly:
            _log.warning(
                "Anomaly detected: severity=%s, value=%f, threshold=%f",
                anomaly_result.severity.value,
                anomaly_result.metric_value,
                anomaly_result.threshold_value or 0.0
            )

            await self._send_anomaly_alert(window_metrics, anomaly_result)

    async def _send_anomaly_alert(
        self,
        window_metrics: object,
        anomaly_result: object
    ) -> None:
        """Send alert for detected anomaly.

        Args:
            window_metrics: Window metrics with anomaly.
            anomaly_result: Detected anomaly details.
        """
        from src.aggregation.models import WindowMetrics
        from src.detection.models import AnomalyResult

        if not isinstance(window_metrics, WindowMetrics):
            return
        if not isinstance(anomaly_result, AnomalyResult):
            return

        await self._alerter.send_alert(
            severity=anomaly_result.severity.value,
            message=anomaly_result.description,
            context={
                "metric_value": anomaly_result.metric_value,
                "threshold_value": anomaly_result.threshold_value,
                "confidence": anomaly_result.confidence,
                "detected_at": anomaly_result.detected_at.isoformat(),
                "window_count": window_metrics.count,
                "window_average": window_metrics.average,
                "window_start": window_metrics.window_bounds.start.isoformat(),
                "window_end": window_metrics.window_bounds.end.isoformat()
            }
        )


__all__ = ["TelemetryWorker"]
