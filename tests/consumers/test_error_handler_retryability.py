"""Complete tests for ConsumerErrorHandler retryability."""

import asyncio

import pytest
from redis.exceptions import BusyLoadingError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from src.consumers.deserializer import DeserializationError
from src.consumers.error_handler import ConsumerErrorHandler
from src.consumers.exceptions import ConsumerError


class TestConsumerErrorHandlerRetryability:
    """Test error handler retry logic and retryability."""

    @pytest.fixture
    def handler(self) -> ConsumerErrorHandler:
        """Create error handler.

        Returns:
            ConsumerErrorHandler instance.
        """
        return ConsumerErrorHandler(max_retries=3, base_delay=0.01, max_delay=0.1)

    def test_is_retryable_connection_error(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test ConnectionError is retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(ConnectionError()) is True

    def test_is_retryable_timeout_error(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test TimeoutError is retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(TimeoutError()) is True

    def test_is_retryable_asyncio_timeout(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test asyncio.TimeoutError is retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(asyncio.TimeoutError()) is True

    def test_is_retryable_redis_connection_error(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test Redis ConnectionError is retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(RedisConnectionError()) is True

    def test_is_retryable_redis_timeout(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test Redis TimeoutError is retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(RedisTimeoutError()) is True

    def test_is_retryable_busy_loading_error(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test BusyLoadingError is retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(BusyLoadingError()) is True

    def test_is_not_retryable_deserialization_error(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test DeserializationError is not retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(DeserializationError("Invalid")) is False

    def test_is_not_retryable_value_error(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test ValueError is not retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(ValueError("Invalid")) is False

    def test_is_not_retryable_type_error(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test TypeError is not retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(TypeError("Invalid")) is False

    def test_is_retryable_unknown_error_defaults_true(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test unknown error defaults to retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """
        assert handler.is_retryable(RuntimeError("Unknown")) is True

    async def test_with_retry_non_retryable_error_raises(
        self,
        handler: ConsumerErrorHandler,
    ) -> None:
        """Test with_retry raises ConsumerError for non-retryable.

        Args:
            handler: ConsumerErrorHandler fixture.
        """

        async def failing_operation(data):
            raise ValueError("Non-retryable")

        with pytest.raises(ConsumerError, match="Non-retryable error occurred"):
            await handler.with_retry(
                operation=failing_operation,
                message_id="test-123",
                data={"test": "data"},
            )


__all__: list[str] = []
