"""Error handling and retry logic for stream consumers.

Class:
    ConsumerErrorHandler: Handles errors and retries for message processing.
"""

import logging
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any, TypeVar

from src.processor.exceptions import (
    DeserializationError,
    MaxRetriesExceededError,
    ProcessorError,
)

_log = logging.getLogger(__name__)

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

    __slots__ = ("_max_retries", "_base_delay", "_max_delay")

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
        raise NotImplementedError

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
            MaxRetriesExceededError: If all retry attempts fail.
            ProcessorError: For non-retryable errors.

        Example:
            async def parse_event(raw_data):
                return TelemetryEvent(**raw_data)

            event = await handler.with_retry(
                operation=parse_event,
                message_id="msg-456",
                data={"device_id": "router-01", ...}
            )
        """
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError


__all__ = ["ConsumerErrorHandler"]
