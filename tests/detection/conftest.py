"""Detection library test fixtures.

Provides test fixtures specific to detection library testing including
sample window metrics, threshold configurations, and expected anomalies.
"""

from datetime import datetime, timezone

import pytest

from src.aggregation.models import WindowBounds, WindowMetrics


@pytest.fixture
def sample_window_bounds() -> WindowBounds:
    """Sample WindowBounds for testing.

    Returns:
        WindowBounds instance with realistic values.
    """
    window_bounds = WindowBounds(
        start=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        end=datetime(2024, 1, 1, 12, 1, 0, tzinfo=timezone.utc),
        size_seconds=60.0,
    )
    return window_bounds


@pytest.fixture
def sample_window_metrics(sample_window_bounds: WindowBounds) -> WindowMetrics:
    """Sample WindowMetrics for detection testing.

    Returns:
        WindowMetrics instance with realistic values

    Example:
        def test_detector(sample_window_metrics):
            result = detector.detect(sample_window_metrics)
            assert result.is_anomaly
    """
    sample_metrics = WindowMetrics(
        device_id="router-01",
        interface="eth0",
        metric_name="cpu_utilization",
        window_bounds=sample_window_bounds,
        average=85.5,
        minimum=75.0,
        maximum=95.0,
        stddev=5.2,
        count=120,
        sum=10260.0,
    )
    return sample_metrics


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
    config = {
        "cpu_utilization": 80.0,
        "bandwidth_utilization": 90.0,
        "error_rate": 1.0,
    }
    return config


@pytest.fixture
def normal_metrics(sample_window_bounds: WindowBounds) -> WindowMetrics:
    """Window metrics with normal (non-anomalous) values.

    Returns:
        WindowMetrics with values below thresholds

    Example:
        def test_no_anomaly(normal_metrics):
            result = detector.detect(normal_metrics)
            assert not result.is_anomaly
    """
    normal_values = WindowMetrics(
        device_id="router-02",
        interface="eth1",
        metric_name="cpu_utilization",
        window_bounds=sample_window_bounds,
        average=65.0,
        minimum=55.0,
        maximum=75.0,
        stddev=4.5,
        count=100,
        sum=6500.0,
    )
    return normal_values


@pytest.fixture
def anomalous_metrics(sample_window_bounds: WindowBounds) -> WindowMetrics:
    """Window metrics with anomalous values.

    Returns:
        WindowMetrics with values exceeding thresholds

    Example:
        def test_detects_anomaly(anomalous_metrics):
            result = detector.detect(anomalous_metrics)
            assert result.is_anomaly
    """
    anomalous_values = WindowMetrics(
        device_id="router-03",
        interface="eth2",
        metric_name="cpu_utilization",
        window_bounds=sample_window_bounds,
        average=95.5,
        minimum=85.0,
        maximum=99.0,
        stddev=3.2,
        count=110,
        sum=10505.0,
    )
    return anomalous_values
