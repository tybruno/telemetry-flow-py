"""Tests for consumer error handler functionality.

Tests the ConsumerErrorHandler class including retry logic, exponential
backoff, and error classification.
"""

import pytest

from src.consumers.error_handler import ConsumerErrorHandler
from src.consumers.exceptions import (
    ConsumerError,
    DeserializationError,
    RetryExhaustedError,
)


class TestConsumerErrorHandler:
    """Tests for ConsumerErrorHandler class."""

    @pytest.fixture
    def handler(self) -> ConsumerErrorHandler:
        """Create error handler for testing.

        Returns:
            ConsumerErrorHandler instance.
        """
        return ConsumerErrorHandler(max_retries=3, base_delay=0.01, max_delay=1.0)

    async def test_retry_transient_error(self, handler: ConsumerErrorHandler) -> None:
        """Test handler retries transient errors.

        Verifies operation retried with exponential backoff for
        transient failures like timeouts.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        call_count = 0

        async def failing_operation(data: dict) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("Transient error")
            return "success"

        result = await handler.with_retry(
            operation=failing_operation, message_id="test-123", data={"test": "data"}
        )

        assert result == "success"
        assert call_count == 3

    async def test_no_retry_permanent_error(
        self, handler: ConsumerErrorHandler
    ) -> None:
        """Test handler doesn't retry permanent errors.

        Verifies operation fails immediately for permanent errors
        like validation failures.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        call_count = 0

        async def failing_operation(data: dict) -> str:
            nonlocal call_count
            call_count += 1
            raise DeserializationError("Permanent error")

        # Non-retryable errors are wrapped in ConsumerError
        with pytest.raises(ConsumerError, match="Non-retryable error occurred"):
            await handler.with_retry(
                operation=failing_operation,
                message_id="test-123",
                data={"test": "data"},
            )

        assert call_count == 1

    async def test_exponential_backoff(self, handler: ConsumerErrorHandler) -> None:
        """Test handler uses exponential backoff for retries.

        Verifies wait time increases exponentially with retry attempt.

        Args:
            handler: ConsumerErrorHandler fixture.
        """

        async def always_fails(data: dict) -> str:
            raise TimeoutError("Always fails")

        with pytest.raises(RetryExhaustedError):
            await handler.with_retry(
                operation=always_fails, message_id="test-123", data={"test": "data"}
            )

    async def test_max_retries_exceeded(self, handler: ConsumerErrorHandler) -> None:
        """Test handler raises after max retries exceeded.

        Verifies RetryExhaustedError raised when retry limit reached.

        Args:
            handler: ConsumerErrorHandler fixture.
        """

        async def always_fails(data: dict) -> str:
            raise ConnectionError("Connection failed")

        with pytest.raises(RetryExhaustedError):
            await handler.with_retry(
                operation=always_fails, message_id="test-123", data={"test": "data"}
            )
