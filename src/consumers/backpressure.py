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
        raise NotImplementedError

    async def should_throttle(self) -> bool:
        """Check if consumer should throttle due to backpressure.

        Returns:
            True if consumer should wait before processing more messages

        Example:
            if await manager.should_throttle():
                await asyncio.sleep(0.1)
        """
        raise NotImplementedError

    async def wait(self) -> None:
        """Wait until backpressure condition clears.

        Blocks until tokens are available for processing. Uses exponential
        backoff for successive waits.

        Example:
            await manager.wait()  # Blocks until ready
        """
        raise NotImplementedError

    async def record_processed(self) -> None:
        """Record that a message was successfully processed.

        Updates internal counters for rate calculation and backpressure
        detection.

        Example:
            await process_message(msg)
            await manager.record_processed()
        """
        raise NotImplementedError


__all__ = ["BackpressureManager"]
