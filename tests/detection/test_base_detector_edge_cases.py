"""Edge case tests for BaseDetector."""

import math
from datetime import datetime, timezone

import pytest

from src.aggregation.models import WindowBounds, WindowMetrics
from src.detection.base_detector import BaseDetector
from src.detection.models import AnomalyResult


class ConcreteDetector(BaseDetector):
    """Concrete implementation for testing."""

    def detect(self, metric: WindowMetrics) -> AnomalyResult | None:
        """Test implementation."""
        self._validate_metric(metric)
        return None


class TestBaseDetectorValidation:
    """Test BaseDetector validation methods."""

    @pytest.fixture
    def detector(self) -> ConcreteDetector:
        """Create detector instance.

        Returns:
            ConcreteDetector instance.
        """
        return ConcreteDetector()

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

    def test_validate_metric_with_infinite_average_raises(
        self,
        detector: ConcreteDetector,
        bounds: WindowBounds,
    ) -> None:
        """Test _validate_metric raises on infinite average.

        Args:
            detector: ConcreteDetector fixture.
            bounds: WindowBounds fixture.
        """
        metric = WindowMetrics(
            window_bounds=bounds,
            average=math.inf,
            minimum=70.0,
            maximum=90.0,
            stddev=5.0,
            count=10,
            sum=800.0,
        )

        with pytest.raises(ValueError, match="Metric average must be finite"):
            detector._validate_metric(metric)

    def test_validate_metric_with_nan_average_raises(
        self,
        detector: ConcreteDetector,
        bounds: WindowBounds,
    ) -> None:
        """Test _validate_metric raises on NaN average.

        Args:
            detector: ConcreteDetector fixture.
            bounds: WindowBounds fixture.
        """
        metric = WindowMetrics(
            window_bounds=bounds,
            average=math.nan,
            minimum=70.0,
            maximum=90.0,
            stddev=5.0,
            count=10,
            sum=800.0,
        )

        with pytest.raises(ValueError, match="Metric average must be finite"):
            detector._validate_metric(metric)

    def test_validate_metric_with_zero_count_raises(
        self,
        detector: ConcreteDetector,
        bounds: WindowBounds,
    ) -> None:
        """Test _validate_metric raises on zero count.

        Args:
            detector: ConcreteDetector fixture.
            bounds: WindowBounds fixture.
        """
        metric = WindowMetrics(
            window_bounds=bounds,
            average=80.0,
            minimum=70.0,
            maximum=90.0,
            stddev=5.0,
            count=0,
            sum=0.0,
        )

        with pytest.raises(ValueError, match="Metric count must be positive"):
            detector._validate_metric(metric)

    def test_validate_metric_with_negative_count_raises(
        self,
        detector: ConcreteDetector,
        bounds: WindowBounds,
    ) -> None:
        """Test _validate_metric raises on negative count.

        Args:
            detector: ConcreteDetector fixture.
            bounds: WindowBounds fixture.
        """
        metric = WindowMetrics(
            window_bounds=bounds,
            average=80.0,
            minimum=70.0,
            maximum=90.0,
            stddev=5.0,
            count=-5,
            sum=400.0,
        )

        with pytest.raises(ValueError, match="Metric count must be positive"):
            detector._validate_metric(metric)


__all__: list[str] = []
