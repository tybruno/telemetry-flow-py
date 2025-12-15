"""Error handling and retry logic for stream consumers.

This module provides robust error handling with exponential backoff retry
logic, error classification, and dead letter handling for failed messages.

Classes:
    ConsumerErrorHandler: Handles errors and retries for message processing.
"""

import asyncio
import logging as _log
import random
from asyncio import TimeoutError as AsyncioTimeoutError
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from redis.exceptions import BusyLoadingError
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError

from src.consumers.exceptions import (
    ConsumerError,
    DeserializationError,
    RetryExhaustedError,
)

T = TypeVar("T")


class ConsumerErrorHandler:
    """Handles errors and implements retry logic for message processing.

    Provides exponential backoff retry logic, error classification, and
    dead letter handling for failed messages that exceed retry limits.

    Attributes:
        _max_retries: Maximum number of retry attempts per message.
        _base_delay: Base delay in seconds for exponential backoff.
        _max_delay: Maximum delay in seconds between retries.

    Example:
        handler = ConsumerErrorHandler(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0
        )

        async def process_message(data):
            # May raise exceptions
            return parse_and_process(data)

        result = await handler.with_retry(
            operation=process_message,
            message_id="msg-123",
            data=raw_data
        )
    """

    __slots__ = ("_base_delay", "_max_delay", "_max_retries")

    _max_retries: int
    _base_delay: float
    _max_delay: float

    def __init__(
        self,
        *,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ) -> None:
        """Initialize error handler with retry configuration.

        Args:
            max_retries: Maximum retry attempts (default: 3).
            base_delay: Base delay for exponential backoff in seconds
                (default: 1.0).
            max_delay: Maximum delay between retries in seconds
                (default: 30.0).

        Raises:
            ValueError: If any parameter is negative.
        """
        self._validate_retry_params(max_retries, base_delay, max_delay)

        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay

    def _validate_retry_params(
        self, max_retries: int, base_delay: float, max_delay: float
    ) -> None:
        """Validate retry configuration parameters.

        Args:
            max_retries: Maximum retry attempts.
            base_delay: Base delay in seconds.
            max_delay: Maximum delay in seconds.

        Raises:
            ValueError: If any parameter is negative.
        """
        if max_retries < 0:
            error_message = "max_retries must be non-negative: %d"
            _log.error(error_message, max_retries)
            raise ValueError(error_message % max_retries) from None

        if base_delay < 0:
            error_message = "base_delay must be non-negative: %f"
            _log.error(error_message, base_delay)
            raise ValueError(error_message % base_delay) from None

        if max_delay < 0:
            error_message = "max_delay must be non-negative: %f"
            _log.error(error_message, max_delay)
            raise ValueError(error_message % max_delay) from None

    async def with_retry(
        self,
        *,
        operation: Callable[[Any], Awaitable[T]],
        message_id: str,
        data: Any,
    ) -> T:
        """Execute operation with automatic retry logic.

        Args:
            operation: Async function to execute with retry.
            message_id: ID of message being processed (for logging).
            data: Data to pass to operation.

        Returns:
            Result from successful operation execution.

        Raises:
            RetryExhaustedError: If all retry attempts fail.
            ConsumerError: For non-retryable errors.

        Example:
            async def parse_event(raw_data):
                return TelemetryEvent(**raw_data)

            event = await handler.with_retry(
                operation=parse_event,
                message_id="msg-456",
                data={"device_id": "router-01", ...}
            )
        """
        last_exception = None

        for attempt in range(self._max_retries + 1):
            try:
                result = await operation(data)

                if attempt > 0:
                    self._log_retry_success(attempt, message_id)

                return result

            except Exception as e:
                last_exception = e

                self._handle_retry_error(e, attempt, message_id)

                if attempt < self._max_retries:
                    delay = self.calculate_delay(attempt)
                    await asyncio.sleep(delay)

        if last_exception:
            raise RetryExhaustedError(
                "All retry attempts exhausted"
            ) from last_exception

        error_message = "Operation failed without exception"
        raise RuntimeError(error_message) from None

    def _log_retry_success(self, attempt: int, message_id: str) -> None:
        """Log successful retry operation.

        Args:
            attempt: Number of attempts made.
            message_id: Message identifier.
        """
        _log.info(
            "Operation succeeded after %d retries for message_id=%s",
            attempt,
            message_id,
        )

    def _handle_retry_error(
        self, error: Exception, attempt: int, message_id: str
    ) -> None:
        """Handle error during retry attempt.

        Args:
            error: Exception that occurred.
            attempt: Current attempt number.
            message_id: Message identifier.

        Raises:
            ConsumerError: If error is not retryable.
        """
        if not self.is_retryable(error):
            _log.error(
                "Non-retryable error for message_id=%s: %s", message_id, str(error)
            )
            raise ConsumerError("Non-retryable error occurred") from error

        if attempt < self._max_retries:
            self._log_retry_attempt(attempt, message_id, error)
        else:
            self._log_retry_exhausted(message_id, error)

    def _log_retry_attempt(
        self, attempt: int, message_id: str, error: Exception
    ) -> None:
        """Log retry attempt details.

        Args:
            attempt: Current attempt number.
            message_id: Message identifier.
            error: Exception that occurred.
        """
        delay = self.calculate_delay(attempt)
        _log.warning(
            "Retry attempt %d/%d for message_id=%s after %0.2fs: %s",
            attempt + 1,
            self._max_retries,
            message_id,
            delay,
            str(error),
        )

    def _log_retry_exhausted(self, message_id: str, error: Exception) -> None:
        """Log retry exhaustion.

        Args:
            message_id: Message identifier.
            error: Exception that occurred.
        """
        _log.error(
            "All retry attempts exhausted for message_id=%s: %s", message_id, str(error)
        )

    def is_retryable(self, error: Exception) -> bool:
        """Determine if error is retryable.

        Args:
            error: Exception that occurred during processing.

        Returns:
            True if error warrants retry, False for permanent failures.

        Example:
            try:
                process_message(data)
            except Exception as e:
                if handler.is_retryable(e):
                    # Retry
                else:
                    # Send to dead letter queue
        """
        # Network and transient errors are retryable
        retryable_types = (
            ConnectionError,
            TimeoutError,
            AsyncioTimeoutError,
            RedisConnectionError,
            RedisTimeoutError,
            BusyLoadingError,
        )

        # DeserializationError is NOT retryable (permanent data issue)
        non_retryable_types = (
            DeserializationError,
            ValueError,
            TypeError,
        )

        if isinstance(error, non_retryable_types):
            is_retryable_error = False
            return is_retryable_error

        if isinstance(error, retryable_types):
            is_retryable_error = True
            return is_retryable_error

        # Unknown errors default to retryable (conservative approach)
        is_retryable_error = True
        return is_retryable_error

    def calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay.

        Args:
            attempt: Current attempt number (0-indexed).

        Returns:
            Delay in seconds before next retry.

        Example:
            delay = handler.calculate_delay(attempt=2)
            await asyncio.sleep(delay)
        """
        # Exponential backoff: base_delay * 2^attempt
        exponential_delay = self._base_delay * (2**attempt)

        # Cap at max_delay
        capped_delay = min(exponential_delay, self._max_delay)

        # Add jitter (± 10%) to prevent thundering herd
        jitter_range = capped_delay * 0.1
        jitter = random.uniform(-jitter_range, jitter_range)  # noqa: S311

        final_delay = capped_delay + jitter

        # Ensure non-negative
        delay_with_floor: float = max(0.0, final_delay)

        return delay_with_floor


__all__ = ["ConsumerErrorHandler"]
