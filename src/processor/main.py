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
    raise NotImplementedError


def main() -> None:
    """Main entry point for the processor service.

    Loads configuration from environment variables and config files,
    then runs the async worker using asyncio.

    Configuration:
        - PROCESSOR_WINDOW_SIZE_SECONDS: Aggregation window size (default: 60)
        - PROCESSOR_DEFAULT_THRESHOLD: Default anomaly threshold (default: 80.0)
        - PROCESSOR_MAX_RETRIES: Max retry attempts for failures (default: 3)
        - PROCESSOR_CONSUMER_GROUP: Consumer group name (default: telemetry-processors)
        - REDIS_URL: Redis connection URL (required)

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
    raise NotImplementedError


if __name__ == "__main__":
    main()


__all__ = ["main", "run_worker"]
