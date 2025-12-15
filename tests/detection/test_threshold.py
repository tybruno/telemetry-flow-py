"""Tests for threshold-based anomaly detector.

Tests the ThresholdDetector class including threshold comparison,
severity classification, and anomaly result generation.
"""

from datetime import datetime, timezone

import pytest

from src.aggregation.models import WindowBounds, WindowMetrics
from src.detection.threshold import ThresholdDetector


class TestThresholdDetector:
    """Tests for ThresholdDetector class."""

    @pytest.fixture
    def detector(self) -> ThresholdDetector:
        """Create threshold detector for testing.

        Returns:
            ThresholdDetector instance.
        """
        return ThresholdDetector(
            thresholds={"cpu_utilization": 90.0},
            default_threshold=80.0,
        )

    def test_threshold_detector_negative_default_threshold_raises(self) -> None:
        """Test ThresholdDetector raises on negative default threshold."""
        with pytest.raises(ValueError, match="Default threshold cannot be negative"):
            ThresholdDetector(thresholds={}, default_threshold=-10.0)

    def test_threshold_detector_negative_threshold_raises(self) -> None:
        """Test ThresholdDetector raises on negative threshold value."""
        with pytest.raises(ValueError, match="Threshold for .* cannot be negative"):
            ThresholdDetector(
                thresholds={"cpu": -50.0},
                default_threshold=80.0,
            )

    @pytest.fixture
    def sample_metric(self) -> WindowMetrics:
        """Create sample metric.

        Returns:
            WindowMetrics instance.
        """
        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0
        )
        metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=75.0,
            minimum=50.0,
            maximum=95.0,
            stddev=10.0,
            count=10,
            sum=750.0
        )
        return metric

    def test_detector_initialization(self) -> None:
        """Test detector initializes with threshold configuration.

        Verifies detector requires threshold dictionary mapping
        metric names to threshold values.
        """
        detector = ThresholdDetector(
            thresholds={"metric1": 90.0, "metric2": 95.0},
            default_threshold=80.0,
        )

        assert detector._thresholds == {"metric1": 90.0, "metric2": 95.0}
        assert detector._default_threshold == 80.0

    def test_detect_no_anomaly(
        self,
        detector: ThresholdDetector,
        sample_metric: WindowMetrics,
    ) -> None:
        """Test detector returns no anomaly for normal metrics.

        Verifies None or AnomalyResult with is_anomaly=False returned
        when metrics below thresholds.

        Args:
            detector: ThresholdDetector fixture.
            sample_metric: Sample metric fixture.
        """
        is_anomaly_result = detector.is_anomaly(sample_metric)
        assert is_anomaly_result is False

    def test_detect_anomaly_threshold_exceeded(
        self,
        detector: ThresholdDetector,
    ) -> None:
        """Test detector detects anomaly when threshold exceeded.

        Verifies AnomalyResult with is_anomaly=True returned when
        metric value exceeds configured threshold.

        Args:
            detector: ThresholdDetector fixture.
        """
        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0
        )
        high_metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=95.0,  # Exceeds 80.0 default threshold
            minimum=90.0,
            maximum=99.0,
            stddev=3.0,
            count=10,
            sum=950.0
        )

        is_anomaly_result = detector.is_anomaly(high_metric)
        assert is_anomaly_result is True

    def test_classify_severity(self, detector: ThresholdDetector) -> None:
        """Test detector classifies anomaly severity correctly.

        Verifies severity increases with how much threshold exceeded
        (e.g., 10% over = MEDIUM, 25% over = HIGH, 50% over = CRITICAL).

        Args:
            detector: ThresholdDetector fixture.
        """
        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0
        )
        # 95.0 vs 90.0 threshold (cpu_utilization in detector fixture) = 5.56% over = low severity
        low_metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=95.0,
            minimum=90.0,
            maximum=99.0,
            stddev=3.0,
            count=10,
            sum=950.0
        )

        result = detector.create_anomaly_result(low_metric)
        assert result.severity.value == "low"
        assert result.confidence == 0.75  # From _calculate_severity for ratio <= 0.1

    def test_confidence_calculation(self, detector: ThresholdDetector) -> None:
        """Test detector calculates confidence score.

        Verifies confidence score (0.0 to 1.0) reflects detection
        certainty based on threshold exceedance.

        Args:
            detector: ThresholdDetector fixture.
        """
        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0
        )
        high_metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=95.0,
            minimum=90.0,
            maximum=99.0,
            stddev=3.0,
            count=10,
            sum=950.0
        )

        result = detector.create_anomaly_result(high_metric)
        assert 0.0 <= result.confidence <= 1.0

    def test_detect_returns_none_for_non_anomaly(
        self,
        detector: ThresholdDetector,
        sample_metric: WindowMetrics,
    ) -> None:
        """Test detect returns None when no anomaly detected.

        Args:
            detector: ThresholdDetector fixture.
            sample_metric: WindowMetrics fixture with value 75.0.
        """
        # sample_metric has average 75.0, below threshold 80.0
        result = detector.detect(sample_metric)
        assert result is None

    def test_missing_threshold_handling(self) -> None:
        """Test detector handles metrics without configured thresholds.

        Verifies graceful handling when no threshold exists for metric.
        """
        detector = ThresholdDetector(
            thresholds={},
            default_threshold=80.0,
        )

        bounds = WindowBounds(
            start=datetime(2025, 12, 12, 10, 0, 0, tzinfo=timezone.utc),
            end=datetime(2025, 12, 12, 10, 1, 0, tzinfo=timezone.utc),
            size_seconds=60.0
        )
        metric = WindowMetrics(
            device_id="router-01",
            interface="eth0",
            metric_name="cpu_utilization",
            window_bounds=bounds,
            average=75.0,
            minimum=50.0,
            maximum=95.0,
            stddev=10.0,
            count=10,
            sum=750.0
        )

        # Should use default threshold
        is_anomaly_result = detector.is_anomaly(metric)
        assert isinstance(is_anomaly_result, bool)
