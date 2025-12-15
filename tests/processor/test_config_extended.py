"""Extended tests for ProcessorConfig validation."""

import pytest
from src.processor.config import ProcessorConfig


class TestProcessorConfigValidation:
    """Tests for ProcessorConfig validation logic."""

    def test_validate_config_rejects_zero_window_size(self) -> None:
        """Test validate_config raises on window_size of 0."""
        config = ProcessorConfig(
            window_size_seconds=0,
            consumer_group="test",
            redis_url="redis://localhost"
        )
        
        with pytest.raises(ValueError, match="Invalid window_size_seconds"):
            config.validate_config()

    def test_validate_config_rejects_negative_window_size(self) -> None:
        """Test validate_config raises on negative window_size."""
        config = ProcessorConfig(
            window_size_seconds=-10,
            consumer_group="test",
            redis_url="redis://localhost"
        )
        
        with pytest.raises(ValueError, match="Invalid window_size_seconds"):
            config.validate_config()

    def test_validate_config_rejects_negative_max_retries(self) -> None:
        """Test validate_config raises on negative max_retries."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            max_retries=-1
        )
        
        with pytest.raises(ValueError, match="Invalid max_retries"):
            config.validate_config()

    def test_validate_config_rejects_negative_default_threshold(self) -> None:
        """Test validate_config raises on negative default_threshold."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            default_threshold=-5.0
        )
        
        with pytest.raises(ValueError, match="Invalid default_threshold"):
            config.validate_config()

    def test_validate_config_rejects_partition_id_without_num_partitions(
        self
    ) -> None:
        """Test validate_config raises on partition_id without num_partitions."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            partition_id=1
        )
        
        with pytest.raises(
            ValueError,
            match="num_partitions required when partition_id is set"
        ):
            config.validate_config()

    def test_validate_config_rejects_negative_partition_id(self) -> None:
        """Test validate_config raises on negative partition_id."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            partition_id=-1,
            num_partitions=4
        )
        
        with pytest.raises(
            ValueError,
            match="Invalid partition_id"
        ):
            config.validate_config()

    def test_validate_config_rejects_partition_id_equal_to_num_partitions(
        self
    ) -> None:
        """Test validate_config raises on partition_id >= num_partitions."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            partition_id=4,
            num_partitions=4
        )
        
        with pytest.raises(
            ValueError,
            match="Invalid partition_id"
        ):
            config.validate_config()

    def test_validate_config_rejects_partition_id_greater_than_num_partitions(
        self
    ) -> None:
        """Test validate_config raises on partition_id > num_partitions."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            partition_id=10,
            num_partitions=4
        )
        
        with pytest.raises(
            ValueError,
            match="Invalid partition_id"
        ):
            config.validate_config()

    def test_validate_config_rejects_negative_metric_threshold(self) -> None:
        """Test validate_config raises on negative metric threshold."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            metric_thresholds={"cpu_usage": -10.0}
        )
        
        with pytest.raises(
            ValueError,
            match="Invalid threshold for cpu_usage"
        ):
            config.validate_config()

    def test_validate_config_accepts_valid_configuration(self) -> None:
        """Test validate_config succeeds with valid config."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            max_retries=3,
            default_threshold=80.0,
            partition_id=2,
            num_partitions=4,
            metric_thresholds={"cpu_usage": 90.0}
        )
        
        # Should not raise
        config.validate_config()

    def test_validate_config_accepts_zero_max_retries(self) -> None:
        """Test validate_config accepts max_retries of 0."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            max_retries=0
        )
        
        # Should not raise
        config.validate_config()

    def test_validate_config_accepts_zero_default_threshold(self) -> None:
        """Test validate_config accepts default_threshold of 0."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            default_threshold=0.0
        )
        
        # Should not raise
        config.validate_config()


class TestGetStreamName:
    """Tests for get_stream_name method."""

    def test_get_stream_name_without_partitioning(self) -> None:
        """Test get_stream_name returns stream name without partitioning."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            stream_name="telemetry"
        )
        
        stream_name = config.get_stream_name()
        
        assert stream_name == "telemetry"

    def test_get_stream_name_with_partitioning(self) -> None:
        """Test get_stream_name returns partitioned stream name."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            stream_name="telemetry",
            partition_id=2,
            num_partitions=4
        )
        
        stream_name = config.get_stream_name()
        
        assert stream_name == "telemetry:2"

    def test_get_stream_name_with_partition_zero(self) -> None:
        """Test get_stream_name with partition_id of 0."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            stream_name="telemetry",
            partition_id=0,
            num_partitions=4
        )
        
        stream_name = config.get_stream_name()
        
        assert stream_name == "telemetry:0"


class TestGetThreshold:
    """Tests for get_threshold method."""

    def test_get_threshold_returns_metric_specific_threshold(self) -> None:
        """Test get_threshold returns metric-specific threshold."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            default_threshold=80.0,
            metric_thresholds={
                "cpu_usage": 90.0,
                "memory_usage": 85.0
            }
        )
        
        threshold = config.get_threshold("cpu_usage")
        
        assert threshold == 90.0

    def test_get_threshold_returns_default_for_unknown_metric(self) -> None:
        """Test get_threshold returns default for unknown metric."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            default_threshold=80.0,
            metric_thresholds={"cpu_usage": 90.0}
        )
        
        threshold = config.get_threshold("network_throughput")
        
        assert threshold == 80.0

    def test_get_threshold_returns_default_with_no_metric_thresholds(
        self
    ) -> None:
        """Test get_threshold returns default when no metric_thresholds set."""
        config = ProcessorConfig(
            window_size_seconds=60,
            consumer_group="test",
            redis_url="redis://localhost",
            default_threshold=75.0
        )
        
        threshold = config.get_threshold("any_metric")
        
        assert threshold == 75.0
