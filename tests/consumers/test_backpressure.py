"""Tests for backpressure manager functionality.

Tests the BackpressureManager class including rate limiting, throttling,
and token bucket algorithm implementation.
"""

import asyncio

import pytest

from src.consumers.backpressure import BackpressureManager


class TestBackpressureManager:
    """Tests for BackpressureManager class."""

    @pytest.fixture
    def manager(self) -> BackpressureManager:
        """Create backpressure manager for testing.

        Returns:
            BackpressureManager instance.
        """
        return BackpressureManager(max_rate=10, window_seconds=1.0)

    def test_manager_initialization(self) -> None:
        """Test backpressure manager initializes with rate config.

        Verifies manager requires max_rate and window_seconds.
        """
        manager = BackpressureManager(max_rate=100, window_seconds=1.0)
        assert manager._max_rate == 100
        assert manager._window_seconds == 1.0
        assert manager._tokens == 100.0

    def test_manager_negative_max_rate_raises(self) -> None:
        """Test BackpressureManager raises on negative max_rate."""
        with pytest.raises(ValueError, match="max_rate must be positive"):
            BackpressureManager(max_rate=-10, window_seconds=1.0)

    def test_manager_zero_max_rate_raises(self) -> None:
        """Test BackpressureManager raises on zero max_rate."""
        with pytest.raises(ValueError, match="max_rate must be positive"):
            BackpressureManager(max_rate=0, window_seconds=1.0)

    def test_manager_negative_window_seconds_raises(self) -> None:
        """Test BackpressureManager raises on negative window_seconds."""
        with pytest.raises(ValueError, match="window_seconds must be positive"):
            BackpressureManager(max_rate=10, window_seconds=-1.0)

    def test_manager_zero_window_seconds_raises(self) -> None:
        """Test BackpressureManager raises on zero window_seconds."""
        with pytest.raises(ValueError, match="window_seconds must be positive"):
            BackpressureManager(max_rate=10, window_seconds=0.0)

    async def test_should_throttle_when_overloaded(
        self,
        manager: BackpressureManager,
    ) -> None:
        """Test manager detects when throttling needed.

        Verifies should_throttle returns True when processing rate
        exceeds configured maximum.

        Args:
            manager: BackpressureManager fixture.
        """
        # Deplete all tokens
        for _ in range(10):
            await manager.record_processed()

        # Should throttle when tokens exhausted
        should_throttle_result = await manager.should_throttle()
        assert should_throttle_result is True

    async def test_wait_until_tokens_available(
        self,
        manager: BackpressureManager,
    ) -> None:
        """Test manager waits until capacity available.

        Verifies wait() blocks until tokens replenished.

        Args:
            manager: BackpressureManager fixture.
        """
        # Deplete tokens
        for _ in range(10):
            await manager.record_processed()

        # Wait should not hang (tokens refill automatically)
        await asyncio.wait_for(manager.wait(), timeout=2.0)
        
        # After waiting, should have tokens available
        assert manager._tokens > 0
        for _ in range(10):
            await manager.record_processed()

        # Wait should complete quickly as tokens refill
        await asyncio.wait_for(manager.wait(), timeout=2.0)

    async def test_record_processed_updates_counters(
        self,
        manager: BackpressureManager,
    ) -> None:
        """Test recording processed messages updates rate tracking.

        Verifies record_processed() increments counters correctly.

        Args:
            manager: BackpressureManager fixture.
        """
        initial_tokens = manager._tokens

        await manager.record_processed()

        # Tokens should decrease
        assert manager._tokens < initial_tokens
