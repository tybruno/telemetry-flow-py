"""Detection library test fixtures.

Provides test fixtures specific to detection library testing including
sample window metrics, threshold configurations, and expected anomalies.
"""
import pytest
from datetime import datetime, UTC
from src.aggregation.models import WindowMetrics, WindowBounds


@pytest.fixture
def sample_window_metrics() -> WindowMetrics:
    """Sample WindowMetrics for detection testing.
    
    Returns:
        WindowMetrics instance with realistic values
        
    Example:
        def test_detector(sample_window_metrics):
            result = detector.detect(sample_window_metrics)
            assert result.is_anomaly
    """
    raise NotImplementedError


@pytest.fixture
def threshold_config() -> dict[str, float]:
    """Threshold configuration for testing.
    
    Returns:
        Dictionary mapping metric names to threshold values
        
    Example:
        def test_threshold_detector(threshold_config):
            detector = ThresholdDetector(thresholds=threshold_config)
            assert detector.get_threshold("cpu") == 80.0
    """
    raise NotImplementedError


@pytest.fixture
def normal_metrics() -> WindowMetrics:
    """Window metrics with normal (non-anomalous) values.
    
    Returns:
        WindowMetrics with values below thresholds
        
    Example:
        def test_no_anomaly(normal_metrics):
            result = detector.detect(normal_metrics)
            assert not result.is_anomaly
    """
    raise NotImplementedError


@pytest.fixture
def anomalous_metrics() -> WindowMetrics:
    """Window metrics with anomalous values.
    
    Returns:
        WindowMetrics with values exceeding thresholds
        
    Example:
        def test_detects_anomaly(anomalous_metrics):
            result = detector.detect(anomalous_metrics)
            assert result.is_anomaly
    """
    raise NotImplementedError
