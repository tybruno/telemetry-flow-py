"""Edge case tests for ConsumerErrorHandler."""

import pytest

from src.consumers.error_handler import ConsumerErrorHandler


class TestConsumerErrorHandlerValidation:
    """Test ConsumerErrorHandler validation."""

    def test_negative_max_retries_raises(self) -> None:
        """Test ConsumerErrorHandler raises on negative max_retries."""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            ConsumerErrorHandler(max_retries=-1, base_delay=1.0, max_delay=10.0)

    def test_negative_base_delay_raises(self) -> None:
        """Test ConsumerErrorHandler raises on negative base_delay."""
        with pytest.raises(ValueError, match="base_delay must be non-negative"):
            ConsumerErrorHandler(max_retries=3, base_delay=-1.0, max_delay=10.0)

    def test_negative_max_delay_raises(self) -> None:
        """Test ConsumerErrorHandler raises on negative max_delay."""
        with pytest.raises(ValueError, match="max_delay must be non-negative"):
            ConsumerErrorHandler(max_retries=3, base_delay=1.0, max_delay=-10.0)


__all__: list[str] = []
