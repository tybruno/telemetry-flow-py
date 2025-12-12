"""Tests for threshold-based anomaly detector.

Tests the ThresholdDetector class including threshold comparison,
severity classification, and anomaly result generation.
"""


class TestThresholdDetector:
    """Tests for ThresholdDetector class."""

    def test_detector_initialization(self) -> None:
        """Test detector initializes with threshold configuration.

        Verifies detector requires threshold dictionary mapping
        metric names to threshold values.
        """
        raise NotImplementedError

    def test_detect_no_anomaly(self) -> None:
        """Test detector returns no anomaly for normal metrics.

        Verifies None or AnomalyResult with is_anomaly=False returned
        when metrics below thresholds.
        """
        raise NotImplementedError

    def test_detect_anomaly_threshold_exceeded(self) -> None:
        """Test detector detects anomaly when threshold exceeded.

        Verifies AnomalyResult with is_anomaly=True returned when
        metric value exceeds configured threshold.
        """
        raise NotImplementedError

    def test_classify_severity(self) -> None:
        """Test detector classifies anomaly severity correctly.

        Verifies severity increases with how much threshold exceeded
        (e.g., 10% over = HIGH, 50% over = CRITICAL).
        """
        raise NotImplementedError

    def test_confidence_calculation(self) -> None:
        """Test detector calculates confidence score.

        Verifies confidence score (0.0 to 1.0) reflects detection
        certainty based on threshold exceedance.
        """
        raise NotImplementedError

    def test_missing_threshold_handling(self) -> None:
        """Test detector handles metrics without configured thresholds.

        Verifies graceful handling when no threshold exists for metric.
        """
        raise NotImplementedError
