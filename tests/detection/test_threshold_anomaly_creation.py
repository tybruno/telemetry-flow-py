"""Comprehensive tests for ThresholdDetector anomaly creation."""

from datetime import datetime, timezone

import pytest

from src.aggregation.models import WindowBounds, WindowMetrics
from src.detection.threshold import ThresholdDetector


class TestThresholdDetectorAnomalyCreation:
    """Test anomaly result creation and severity calculation."""

    @pytest.fixture
    def detector(self) -> ThresholdDetector:
        """Create detector with 80.0 threshold.

        Returns:
            ThresholdDetector instance.
        """
        return ThresholdDetector(thresholds={}, default_threshold=80.0)

    @pytest.fixture
    def bounds(self) -> WindowBounds:
        """Create window bounds.

        Returns:
            WindowBounds instance.
        """
        return WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0,
        )

    def test_create_anomaly_result_with_non_anomaly_raises(
        self,
        detector: ThresholdDetector,
        bounds: WindowBounds,
    ) -> None:
        """Test create_anomaly_result raises when value doesn't exceed threshold.

        Args:
            detector: ThresholdDetector fixture.
            bounds: WindowBounds fixture.
        """
        # Metric with average 75.0, below threshold 80.0
        metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=75.0,
            minimum=70.0,
            maximum=80.0,
            stddev=3.0,
            count=10,
            sum=750.0,
        )

        with pytest.raises(ValueError, match="Metric does not represent an anomaly"):
            detector.create_anomaly_result(metric)

    def test_create_anomaly_critical_severity(
        self,
        detector: ThresholdDetector,
        bounds: WindowBounds,
    ) -> None:
        """Test critical severity for excess > 50%.

        Args:
            detector: ThresholdDetector fixture.
            bounds: WindowBounds fixture.
        """
        # average=140, threshold=80, excess_ratio=(140-80)/80 = 0.75 > 0.5
        metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=140.0,
            minimum=130.0,
            maximum=150.0,
            stddev=5.0,
            count=10,
            sum=1400.0,
        )

        result = detector.create_anomaly_result(metric)
        assert result.severity.value == "critical"
        assert result.confidence == 1.0

    def test_create_anomaly_high_severity(
        self,
        detector: ThresholdDetector,
        bounds: WindowBounds,
    ) -> None:
        """Test high severity for 25% < excess <= 50%.

        Args:
            detector: ThresholdDetector fixture.
            bounds: WindowBounds fixture.
        """
        # average=110, threshold=80, excess_ratio=(110-80)/80 = 0.375
        metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=110.0,
            minimum=105.0,
            maximum=115.0,
            stddev=3.0,
            count=10,
            sum=1100.0,
        )

        result = detector.create_anomaly_result(metric)
        assert result.severity.value == "high"
        assert result.confidence == 0.95

    def test_create_anomaly_medium_severity(
        self,
        detector: ThresholdDetector,
        bounds: WindowBounds,
    ) -> None:
        """Test medium severity for 10% < excess <= 25%.

        Args:
            detector: ThresholdDetector fixture.
            bounds: WindowBounds fixture.
        """
        # average=95, threshold=80, excess_ratio=(95-80)/80 = 0.1875
        metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=95.0,
            minimum=90.0,
            maximum=100.0,
            stddev=3.0,
            count=10,
            sum=950.0,
        )

        result = detector.create_anomaly_result(metric)
        assert result.severity.value == "medium"
        assert result.confidence == 0.85

    def test_create_anomaly_low_severity(
        self,
        detector: ThresholdDetector,
        bounds: WindowBounds,
    ) -> None:
        """Test low severity for excess <= 10%.

        Args:
            detector: ThresholdDetector fixture.
            bounds: WindowBounds fixture.
        """
        # average=85, threshold=80, excess_ratio=(85-80)/80 = 0.0625
        metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=85.0,
            minimum=82.0,
            maximum=88.0,
            stddev=2.0,
            count=10,
            sum=850.0,
        )

        result = detector.create_anomaly_result(metric)
        assert result.severity.value == "low"
        assert result.confidence == 0.75


__all__: list[str] = []
