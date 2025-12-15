"""Processor worker entry point.

Main entry point for running telemetry processor workers that consume
events from Redis Streams, aggregate metrics in time windows, detect
anomalies, and send alerts.

Architecture:
    - Consumes from Redis Streams ("telemetry" stream)
    - Uses consumer group "telemetry-processors" for load balancing
    - Aggregates metrics in configurable time windows (default: 60s)
    - Detects anomalies using threshold-based detection
    - Persists state to Redis Storage
    - Sends alerts via configured alerter

Communication:
    Input: Consumes from Redis Streams (published by Ingest service)
    Output:
        - Stores aggregated metrics to Redis Storage
        - Sends alerts via AlerterProtocol (console, email, etc.)

Functions:
    run_worker: Initialize and run the processor worker.
    main: Entry point for the service.

Example:
    Running the worker::

        # Via Python module (recommended)
        python -m src.processor

        # Direct module execution
        python -m src.processor.main

        # Console script (after pip install -e .)
        telemetry-processor

        # Via Docker Compose
        docker-compose up processor

        # Scale workers for parallel processing
        docker-compose up --scale processor=3
"""

import asyncio
import logging as _log
import os
import sys
import uuid
from typing import cast

from src.aggregation.tumbling_window import TumblingWindowAggregator
from src.alerts.console import ConsoleAlerter
from src.consumers.backpressure import BackpressureManager
from src.consumers.consumer import TelemetryConsumer
from src.consumers.deserializer import MessageDeserializer
from src.consumers.error_handler import ConsumerErrorHandler
from src.core.protocols import AlerterProtocol, StorageProtocol, StreamProtocol
from src.detection.threshold import ThresholdDetector
from src.processor.config import ProcessorConfig
from src.processor.worker import TelemetryWorker
from src.storage.redis_store import RedisStore
from src.streams.redis_stream import RedisStream


async def run_worker() -> None:
    """Run the telemetry processor worker.

    Initializes all pipeline components (consumer, aggregator, detector,
    storage, alerter) and starts consuming events from Redis Streams.
    Runs until interrupted (Ctrl+C) or error occurs.

    Components Initialized:
        - TelemetryConsumer: Robust stream consumer with retry logic
        - TumblingWindowAggregator: Time-windowed metric aggregation
        - ThresholdDetector: Anomaly detection using metric thresholds
        - RedisStore: State persistence for window data
        - ConsoleAlerter: Alert delivery (configurable)

    Processing Pipeline:
        1. Consume event from Redis Streams (XREADGROUP)
        2. Deserialize raw message to TelemetryEvent
        3. Aggregate in time window (calculate avg, min, max, stddev)
        4. Detect anomalies against configured thresholds
        5. Store aggregated metrics to Redis
        6. Send alerts for detected anomalies
        7. Acknowledge message (XACK)

    Raises:
        ConfigurationError: If required configuration is missing.
        ConnectionError: If Redis connection fails.

    Example:
        await run_worker()  # Runs until interrupted
    """
    _log.info("Initializing telemetry processor worker")

    # Load configuration
    config = ProcessorConfig()
    config.validate_config()

    # Get stream name (handles partitioning if configured)
    stream_name = config.get_stream_name()

    _log.info(
        "Configuration loaded: window_size=%ds, threshold=%.2f, stream=%s",
        config.window_size_seconds,
        config.default_threshold,
        stream_name,
    )

    if config.partition_id is not None:
        _log.info(
            "Partitioning enabled: partition_id=%d, num_partitions=%d",
            config.partition_id,
            config.num_partitions,
        )

    # Generate unique consumer name for this worker instance
    consumer_name = f"{config.consumer_name_prefix}-{uuid.uuid4().hex[:8]}"

    # Initialize stream connection
    stream = RedisStream(url=config.redis_url)

    # Create consumer group if it doesn't exist
    try:
        await stream.create_consumer_group(
            stream=stream_name,
            group=config.consumer_group,
            start_id="0",  # Process from beginning on first run
        )
        _log.info(
            "Created consumer group: %s for stream: %s",
            config.consumer_group,
            stream_name,
        )
    except Exception as e:
        # Consumer group may already exist, which is fine
        _log.debug("Consumer group setup: %s", str(e))

    # Initialize pipeline components
    deserializer = MessageDeserializer()
    error_handler = ConsumerErrorHandler(max_retries=config.max_retries)
    backpressure = BackpressureManager(max_rate=1000, window_seconds=1)

    consumer = TelemetryConsumer(
        stream=cast(StreamProtocol, stream),
        deserializer=deserializer,
        error_handler=error_handler,
        backpressure=backpressure,
        stream_name=stream_name,
        group_name=config.consumer_group,
        consumer_name=consumer_name,
    )

    aggregator = TumblingWindowAggregator(
        window_size=config.window_size_seconds
    )

    detector = ThresholdDetector(
        thresholds=config.metric_thresholds,
        default_threshold=config.default_threshold,
    )

    storage = RedisStore(url=config.redis_url)
    alerter = cast(AlerterProtocol, ConsoleAlerter())

    # Create and start worker
    worker = TelemetryWorker(
        consumer=consumer,
        aggregator=aggregator,
        detector=detector,
        storage=cast(StorageProtocol, storage),
        alerter=alerter,
    )

    _log.info("Starting worker: %s", consumer_name)

    try:
        await worker.start()
    except KeyboardInterrupt:
        _log.info("Received shutdown signal")
    except Exception as e:
        _log.error("Worker failed with error: %s", str(e))
        raise
    finally:
        await worker.stop()

        # Clean up resources
        try:
            await storage.close()
            await stream.close()
            _log.info("Resources cleaned up")
        except Exception as e:
            _log.error("Error during resource cleanup: %s", str(e))

        _log.info("Worker shutdown complete")


def main() -> int:
    """Main entry point for the processor service.

    Loads configuration from environment variables and config files,
    then runs the async worker using asyncio.

    Configuration:
        - PROCESSOR_WINDOW_SIZE_SECONDS: Aggregation window size (default: 60)
        - PROCESSOR_DEFAULT_THRESHOLD: Default anomaly threshold (default: 80.0)
        - PROCESSOR_MAX_RETRIES: Max retry attempts for failures (default: 3)
        - PROCESSOR_CONSUMER_GROUP: Consumer group name (default: telemetry-processors)
        - REDIS_URL: Redis connection URL (required)

    Returns:
        Exit code:
            - 0: Success - worker shutdown cleanly
            - 1: Configuration error - missing or invalid configuration
            - 2: Connection error - failed to connect to Redis/streams
            - 3: Processing error - unrecoverable error during processing
            - 4: State recovery error - failed to restore worker state

    Example:
        Running with custom configuration::

            # With defaults (recommended)
            python -m src.processor

            # Or with console script
            telemetry-processor

            # With custom window size
            PROCESSOR_WINDOW_SIZE_SECONDS=120 python -m src.processor

            # Multiple workers (scale horizontally)
            docker-compose up --scale processor=3
    """
    # Configure logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging_numeric_level = getattr(_log, log_level.upper(), _log.INFO)

    _log.basicConfig(
        level=logging_numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _log.info("Starting telemetry processor service")

    try:
        # Validate configuration early
        config = ProcessorConfig()
        config.validate_config()

        # Run async worker
        asyncio.run(run_worker())

        _log.info("Processor service shutdown cleanly")
        return 0

    except ValueError as e:
        # Configuration error
        _log.error("Configuration error: %s", str(e))
        return 1

    except ConnectionError as e:
        # Connection error
        _log.error("Connection error: %s", str(e))
        return 2

    except KeyboardInterrupt:
        _log.info("Processor service interrupted by user")
        return 0

    except Exception as e:
        # Processing error
        _log.error("Processor service failed: %s", str(e))
        return 3


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["main", "run_worker"]
