"""Configuration management for processor service.

Class:
    ProcessorConfig: Processor-specific configuration settings.
"""

import logging as _log

from pydantic_settings import BaseSettings


class ProcessorConfig(BaseSettings):
    """Configuration for processor worker service.

    Loads settings from environment variables and config files.
    Uses Pydantic Settings for type-safe configuration management.

    Attributes:
        window_size_seconds: Tumbling window duration in seconds.
        consumer_group: Redis consumer group name.
        consumer_name_prefix: Prefix for consumer instance names.
        max_retries: Maximum message processing retry attempts.
        default_threshold: Default anomaly detection threshold.
        metric_thresholds: Per-metric threshold overrides.
        stream_name: Name of telemetry stream to consume.
        redis_url: Redis connection URL.

    Example:
        # From environment and config file
        config = ProcessorConfig(_env_file="config/processor.yaml")

        aggregator = TumblingWindowAggregator(
            window_size=config.window_size_seconds
        )

        detector = ThresholdDetector(
            thresholds=config.metric_thresholds,
            default_threshold=config.default_threshold
        )
    """

    window_size_seconds: int = 60
    consumer_group: str = "telemetry-processors"
    consumer_name_prefix: str = "processor"
    max_retries: int = 3
    default_threshold: float = 80.0
    metric_thresholds: dict[str, float] = {}
    stream_name: str = "telemetry"
    redis_url: str = "redis://localhost:6379"

    class Config:
        """Pydantic configuration."""

        env_prefix = "PROCESSOR_"
        env_file = "config/processor.yaml"
        extra = "ignore"

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
