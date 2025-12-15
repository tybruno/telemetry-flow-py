"""Tests for BaseDetector abstract method."""

from datetime import datetime, timezone

import pytest

from src.aggregation.models import WindowBounds, WindowMetrics
from src.detection.base_detector import BaseDetector


class AbstractDetectorNoImpl(BaseDetector):
    """Detector without detect implementation."""
    pass


class TestBaseDetectorAbstract:
    """Test BaseDetector abstract method behavior."""

    def test_detect_raises_not_implemented(self) -> None:
        """Test detect raises NotImplementedError if not overridden."""
        # Cannot instantiate abstract class
        with pytest.raises(TypeError, match="abstract"):
            AbstractDetectorNoImpl()


__all__: list[str] = []
