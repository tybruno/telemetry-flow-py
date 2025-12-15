"""Tests for ProcessorConfig validation."""

import pytest

from src.processor.config import ProcessorConfig


class TestProcessorConfigValidation:
    """Test ProcessorConfig validation logic."""

    def test_validate_config_negative_window_size_raises(self) -> None:
        """Test validate_config raises on negative window size."""
        config = ProcessorConfig(window_size_seconds=-60)
        
        with pytest.raises(ValueError, match="Invalid window_size_seconds"):
            config.validate_config()

    def test_validate_config_zero_window_size_raises(self) -> None:
        """Test validate_config raises on zero window size."""
        config = ProcessorConfig(window_size_seconds=0)
        
        with pytest.raises(ValueError, match="Invalid window_size_seconds"):
            config.validate_config()

    def test_validate_config_negative_max_retries_raises(self) -> None:
        """Test validate_config raises on negative max_retries."""
        config = ProcessorConfig(max_retries=-1)
        
        with pytest.raises(ValueError, match="Invalid max_retries"):
            config.validate_config()

    def test_validate_config_negative_default_threshold_raises(self) -> None:
        """Test validate_config raises on negative default_threshold."""
        config = ProcessorConfig(default_threshold=-10.0)
        
        with pytest.raises(ValueError, match="Invalid default_threshold"):
            config.validate_config()

    def test_validate_config_negative_metric_threshold_raises(self) -> None:
        """Test validate_config raises on negative metric threshold."""
        config = ProcessorConfig(
            metric_thresholds={"cpu": -50.0}
        )
        
        with pytest.raises(ValueError, match="Invalid threshold for cpu"):
            config.validate_config()

    def test_validate_config_valid_succeeds(self) -> None:
        """Test validate_config succeeds with valid config."""
        config = ProcessorConfig(
            window_size_seconds=60,
            max_retries=3,
            default_threshold=80.0,
            metric_thresholds={"cpu": 90.0}
        )
        
        # Should not raise
        config.validate_config()

    def test_get_threshold_returns_metric_specific(self) -> None:
        """Test get_threshold returns metric-specific threshold."""
        config = ProcessorConfig(
            default_threshold=80.0,
            metric_thresholds={"cpu": 90.0}
        )
        
        assert config.get_threshold("cpu") == 90.0

    def test_get_threshold_returns_default_for_unknown(self) -> None:
        """Test get_threshold returns default for unknown metric."""
        config = ProcessorConfig(
            default_threshold=80.0,
            metric_thresholds={"cpu": 90.0}
        )
        
        assert config.get_threshold("memory") == 80.0


__all__: list[str] = []
