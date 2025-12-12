"""Tests for consumer error handler functionality.

Tests the ConsumerErrorHandler class including retry logic, exponential
backoff, and error classification.
"""


class TestConsumerErrorHandler:
    """Tests for ConsumerErrorHandler class."""

    async def test_retry_transient_error(self) -> None:
        """Test handler retries transient errors.

        Verifies operation retried with exponential backoff for
        transient failures like timeouts.
        """
        raise NotImplementedError

    async def test_no_retry_permanent_error(self) -> None:
        """Test handler doesn't retry permanent errors.

        Verifies operation fails immediately for permanent errors
        like validation failures.
        """
        raise NotImplementedError

    async def test_exponential_backoff(self) -> None:
        """Test handler uses exponential backoff for retries.

        Verifies wait time increases exponentially with retry attempt.
        """
        raise NotImplementedError

    async def test_max_retries_exceeded(self) -> None:
        """Test handler raises after max retries exceeded.

        Verifies RetryExhaustedError raised when retry limit reached.
        """
        raise NotImplementedError
