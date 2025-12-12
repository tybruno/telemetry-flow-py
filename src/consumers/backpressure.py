"""Backpressure management for stream consumers.

This module provides rate limiting and backpressure management to prevent
consumer overload and ensure system stability under high load conditions.

Classes:
    BackpressureManager: Manages rate limiting and backpressure signals

Example:
    Basic backpressure management::

        manager = BackpressureManager(max_rate=100, window_seconds=1)

        if await manager.should_throttle():
            await manager.wait()

        # Process message
        await manager.record_processed()
"""

import asyncio
import logging as _log
from time import monotonic


class BackpressureManager:
    """Manages rate limiting and backpressure for stream consumers.

    Monitors processing rate and applies throttling when system is overloaded.
    Uses token bucket algorithm for smooth rate limiting.

    Attributes:
        max_rate: Maximum messages per second to process
        window_seconds: Time window for rate calculation
        _tokens: Current available tokens for processing
        _last_refill: Last token refill timestamp

    Example:
        Rate-limited message processing::

            manager = BackpressureManager(max_rate=100, window_seconds=1)

            async for message in consumer.consume():
                if await manager.should_throttle():
                    _log.warning("Backpressure detected, throttling")
                    await manager.wait()

                # Process message
                await process(message)
                await manager.record_processed()
    """

    __slots__ = ("_max_rate", "_window_seconds", "_tokens", "_last_refill")

    _max_rate: int
    _window_seconds: float
    _tokens: float
    _last_refill: float

    def __init__(
        self,
        *,
        max_rate: int,
        window_seconds: float = 1.0
    ) -> None:
        """Initialize backpressure manager.

        Args:
            max_rate: Maximum messages per window to process
            window_seconds: Time window for rate calculation in seconds

        Raises:
            ValueError: If max_rate <= 0 or window_seconds <= 0

        Example:
            manager = BackpressureManager(max_rate=100, window_seconds=1.0)
        """
        self._validate_rate_params(max_rate, window_seconds)

        self._max_rate = max_rate
        self._window_seconds = window_seconds

        self._tokens = float(max_rate)
        self._last_refill = monotonic()

    def _validate_rate_params(
        self,
        max_rate: int,
        window_seconds: float
    ) -> None:
        """Validate rate limiting parameters.

        Args:
            max_rate: Maximum messages per window.
            window_seconds: Time window in seconds.

        Raises:
            ValueError: If parameters are invalid.
        """
        if max_rate <= 0:
            error_message = "max_rate must be positive: %d"
            _log.error(error_message, max_rate)
            raise ValueError(error_message % max_rate) from None

        if window_seconds <= 0:
            error_message = "window_seconds must be positive: %f"
            _log.error(error_message, window_seconds)
            raise ValueError(error_message % window_seconds) from None

    async def should_throttle(self) -> bool:
        """Check if consumer should throttle due to backpressure.

        Returns:
            True if consumer should wait before processing more messages

        Example:
            if await manager.should_throttle():
                await asyncio.sleep(0.1)
        """
        self._refill_tokens()

        # Throttle if we have no tokens available
        should_throttle_now = self._tokens < 1.0
        return should_throttle_now

    async def wait(self) -> None:
        """Wait until backpressure condition clears.

        Blocks until tokens are available for processing. Uses exponential
        backoff for successive waits.

        Example:
            await manager.wait()  # Blocks until ready
        """
        wait_count = 0
        base_wait_time = 0.1

        while await self.should_throttle():
            wait_time = self._calculate_wait_time(wait_count, base_wait_time)

            self._log_backpressure_state(wait_count)

            await asyncio.sleep(wait_time)
            wait_count += 1

        self._log_backpressure_cleared(wait_count)

    def _calculate_wait_time(
        self,
        wait_count: int,
        base_wait_time: float
    ) -> float:
        """Calculate exponential backoff wait time.

        Args:
            wait_count: Number of times waited.
            base_wait_time: Base wait time in seconds.

        Returns:
            Wait time in seconds, capped at 1.0.
        """
        exponential_wait = base_wait_time * (2 ** wait_count)
        capped_wait: float = min(exponential_wait, 1.0)
        return capped_wait

    def _log_backpressure_state(self, wait_count: int) -> None:
        """Log backpressure state.

        Args:
            wait_count: Number of times waited.
        """
        if wait_count == 0:
            _log.debug("Backpressure active, waiting for tokens")

    def _log_backpressure_cleared(self, wait_count: int) -> None:
        """Log when backpressure clears.

        Args:
            wait_count: Total number of times waited.
        """
        if wait_count > 0:
            _log.debug("Backpressure cleared after %d waits", wait_count)

    async def record_processed(self) -> None:
        """Record that a message was successfully processed.

        Updates internal counters for rate calculation and backpressure
        detection.

        Example:
            await process_message(msg)
            await manager.record_processed()
        """
        self._refill_tokens()

        # Consume one token
        if self._tokens >= 1.0:
            self._tokens -= 1.0
        else:
            # Should not happen if should_throttle is used correctly
            self._tokens = 0.0

    def _refill_tokens(self) -> None:
        """Refill token bucket based on elapsed time.

        Internal utility method that adds tokens based on time passed
        since last refill, maintaining the configured rate limit.
        """
        current_time = monotonic()
        elapsed = current_time - self._last_refill

        # Calculate tokens to add based on elapsed time
        # tokens_per_second = max_rate / window_seconds
        tokens_per_second = self._max_rate / self._window_seconds
        tokens_to_add = elapsed * tokens_per_second

        # Add tokens, capped at max_rate
        self._tokens = min(self._tokens + tokens_to_add, float(self._max_rate))

        self._last_refill = current_time


__all__ = ["BackpressureManager"]
