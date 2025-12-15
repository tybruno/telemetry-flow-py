"""Configuration management for processor service.

Class:
    ProcessorConfig: Processor-specific configuration settings.
"""

import logging as _log

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProcessorConfig(BaseSettings):
    """Configuration for processor worker service.

    Loads settings from environment variables and config files.
    Uses Pydantic Settings for type-safe configuration management.

    Supports partitioned stream consumption for horizontal scaling.

    Attributes:
        window_size_seconds: Tumbling window duration in seconds.
        consumer_group: Redis consumer group name.
        consumer_name_prefix: Prefix for consumer instance names.
        max_retries: Maximum message processing retry attempts.
        default_threshold: Default anomaly detection threshold.
        metric_thresholds: Per-metric threshold overrides.
        stream_name: Base name of telemetry streams (without partition suffix).
        redis_url: Redis connection URL.
        partition_id: Optional partition ID for this processor (enables partitioning).
        num_partitions: Total number of partitions (required if partition_id set).

    Example:
        # Single stream (no partitioning)
        config = ProcessorConfig(_env_file="config/processor.yaml")

        # Partitioned stream
        config = ProcessorConfig(
            partition_id=0,
            num_partitions=3,
            _env_file="config/processor.yaml"
        )

        aggregator = TumblingWindowAggregator(
            window_size=config.window_size_seconds
        )

        detector = ThresholdDetector(
            thresholds=config.metric_thresholds,
            default_threshold=config.default_threshold
        )
    """

    model_config = SettingsConfigDict(
        env_prefix="PROCESSOR_",
        env_file="config/processor.yaml",
        extra="ignore",
    )

    window_size_seconds: int = 60
    consumer_group: str = "telemetry-processors"
    consumer_name_prefix: str = "processor"
    max_retries: int = 3
    default_threshold: float = 80.0
    metric_thresholds: dict[str, float] = {}
    stream_name: str = "telemetry"
    redis_url: str = Field(
        default="redis://localhost:6379",
        validation_alias="REDIS_URL",
    )
    partition_id: int | None = None
    num_partitions: int | None = None

    def get_stream_name(self) -> str:
        """Get the stream name for this processor.

        Returns partitioned stream name if partition_id is set,
        otherwise returns base stream name.

        Returns:
            Stream name to consume from.

        Example:
            # No partitioning
            config = ProcessorConfig(stream_name="telemetry")
            assert config.get_stream_name() == "telemetry"

            # With partitioning
            config = ProcessorConfig(
                stream_name="telemetry",
                partition_id=1,
                num_partitions=3
            )
            assert config.get_stream_name() == "telemetry:1"
        """
        if self.partition_id is not None:
            partitioned_stream_name = f"{self.stream_name}:{self.partition_id}"
            return partitioned_stream_name

        stream_name = self.stream_name
        return stream_name

    def validate_config(self) -> None:
        """Validate configuration values.

        Raises:
            ValueError: If configuration is invalid.
        """
        if self.window_size_seconds <= 0:
            error_message = "window_size_seconds must be positive: %d"
            _log.error(error_message, self.window_size_seconds)
            raise ValueError(
                f"Invalid window_size_seconds: {self.window_size_seconds}"
            ) from None

        if self.max_retries < 0:
            error_message = "max_retries cannot be negative: %d"
            _log.error(error_message, self.max_retries)
            raise ValueError(f"Invalid max_retries: {self.max_retries}") from None

        if self.default_threshold < 0:
            error_message = "default_threshold cannot be negative: %f"
            _log.error(error_message, self.default_threshold)
            raise ValueError(
                f"Invalid default_threshold: {self.default_threshold}"
            ) from None

        # Validate partition configuration
        if self.partition_id is not None:
            if self.num_partitions is None:
                error_message = "num_partitions required when partition_id is set"
                _log.error(error_message)
                raise ValueError(error_message) from None

            if self.partition_id < 0 or self.partition_id >= self.num_partitions:
                error_message = "partition_id=%d must be in range [0, %d)"
                _log.error(error_message, self.partition_id, self.num_partitions)
                raise ValueError(
                    f"Invalid partition_id: {self.partition_id} "
                    f"(must be 0 <= partition_id < {self.num_partitions})"
                ) from None

        for metric_name, threshold in self.metric_thresholds.items():
            if threshold < 0:
                error_message = "Threshold for %s cannot be negative: %f"
                _log.error(error_message, metric_name, threshold)
                raise ValueError(
                    f"Invalid threshold for {metric_name}: {threshold}"
                ) from None

    def get_threshold(self, metric_name: str) -> float:
        """Get threshold for specific metric.

        Args:
            metric_name: Name of the metric.

        Returns:
            Metric-specific threshold or default.

        Example:
            threshold = config.get_threshold("bandwidth_utilization")
        """
        threshold_value = self.metric_thresholds.get(
            metric_name, self.default_threshold
        )
        return threshold_value


__all__ = ["ProcessorConfig"]
