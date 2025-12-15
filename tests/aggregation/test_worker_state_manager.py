"""Tests for WorkerStateManager.

This module contains comprehensive tests for worker state persistence
and recovery functionality.
"""

import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.aggregation.window_state import WorkerStateManager
from src.storage.exceptions import StorageError


class TestWorkerStateManagerInitialization:
    """Test WorkerStateManager initialization."""

    def test_initialization_valid(self) -> None:
        """Test manager initializes with valid parameters."""
        storage = MagicMock()
        worker_id = "worker-01"

        manager = WorkerStateManager(storage=storage, worker_id=worker_id)

        assert manager._storage is storage
        assert manager._worker_id == worker_id

    def test_initialization_empty_worker_id_raises(self) -> None:
        """Test initialization with empty worker_id raises ValueError."""
        storage = MagicMock()

        with pytest.raises(ValueError, match="Worker ID cannot be empty"):
            WorkerStateManager(storage=storage, worker_id="")

    def test_initialization_whitespace_worker_id_raises(self) -> None:
        """Test initialization with whitespace worker_id raises ValueError."""
        storage = MagicMock()

        with pytest.raises(ValueError, match="Worker ID cannot be empty"):
            WorkerStateManager(storage=storage, worker_id="   ")

    def test_initialization_logs_info(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test initialization logs worker ID."""
        storage = MagicMock()
        worker_id = "worker-test-01"

        with caplog.at_level(logging.INFO):
            WorkerStateManager(storage=storage, worker_id=worker_id)

        log_messages = [record.message for record in caplog.records]
        assert any("worker_id=worker-test-01" in msg for msg in log_messages)


class TestWorkerStateManagerSaveState:
    """Test WorkerStateManager save_state method."""

    @pytest.mark.asyncio
    async def test_save_state_success(self) -> None:
        """Test saving state successfully."""
        storage = MagicMock()
        storage.set = AsyncMock()
        worker_id = "worker-01"
        manager = WorkerStateManager(storage=storage, worker_id=worker_id)

        state = {
            "last_processed_id": "msg-12345",
            "windows": {"window_1": {"count": 10}},
        }

        await manager.save_state(state)

        storage.set.assert_called_once_with("worker:state:worker-01", state)

    @pytest.mark.asyncio
    async def test_save_state_empty_raises(self) -> None:
        """Test saving empty state raises ValueError."""
        storage = MagicMock()
        manager = WorkerStateManager(storage=storage, worker_id="worker-01")

        with pytest.raises(ValueError, match="State cannot be empty"):
            await manager.save_state({})

    @pytest.mark.asyncio
    async def test_save_state_storage_error_raises(self) -> None:
        """Test storage error during save raises StorageError."""
        storage = MagicMock()
        storage.set = AsyncMock(side_effect=Exception("Redis connection failed"))
        manager = WorkerStateManager(storage=storage, worker_id="worker-01")

        state = {"last_processed_id": "msg-123"}

        with pytest.raises(StorageError, match="Failed to save worker state"):
            await manager.save_state(state)

    @pytest.mark.asyncio
    async def test_save_state_logs_debug(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test save_state logs debug message on success."""
        storage = MagicMock()
        storage.set = AsyncMock()
        manager = WorkerStateManager(storage=storage, worker_id="worker-test")

        state = {"data": "test"}

        with caplog.at_level(logging.DEBUG):
            await manager.save_state(state)

        log_messages = [record.message for record in caplog.records]
        assert any("Worker state saved" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_save_state_logs_error_on_failure(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test save_state logs error on storage failure."""
        storage = MagicMock()
        storage.set = AsyncMock(side_effect=Exception("Connection lost"))
        manager = WorkerStateManager(storage=storage, worker_id="worker-01")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(StorageError):
                await manager.save_state({"data": "test"})

        log_messages = [record.message for record in caplog.records]
        assert any("Failed to save worker state" in msg for msg in log_messages)


class TestWorkerStateManagerLoadState:
    """Test WorkerStateManager load_state method."""

    @pytest.mark.asyncio
    async def test_load_state_success(self) -> None:
        """Test loading state successfully."""
        saved_state = {
            "last_processed_id": "msg-12345",
            "windows": {"window_1": {"count": 10}},
        }
        storage = MagicMock()
        storage.get = AsyncMock(return_value=saved_state)
        manager = WorkerStateManager(storage=storage, worker_id="worker-01")

        result = await manager.load_state()

        assert result == saved_state
        storage.get.assert_called_once_with("worker:state:worker-01")

    @pytest.mark.asyncio
    async def test_load_state_no_state_returns_none(self) -> None:
        """Test loading state when no saved state exists."""
        storage = MagicMock()
        storage.get = AsyncMock(return_value=None)
        manager = WorkerStateManager(storage=storage, worker_id="worker-01")

        result = await manager.load_state()

        assert result is None

    @pytest.mark.asyncio
    async def test_load_state_storage_error_raises(self) -> None:
        """Test storage error during load raises StorageError."""
        storage = MagicMock()
        storage.get = AsyncMock(side_effect=Exception("Connection timeout"))
        manager = WorkerStateManager(storage=storage, worker_id="worker-01")

        with pytest.raises(StorageError, match="Failed to load worker state"):
            await manager.load_state()

    @pytest.mark.asyncio
    async def test_load_state_logs_info_on_found(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test load_state logs info when state is found."""
        storage = MagicMock()
        storage.get = AsyncMock(return_value={"data": "test"})
        manager = WorkerStateManager(storage=storage, worker_id="worker-test")

        with caplog.at_level(logging.INFO):
            await manager.load_state()

        log_messages = [record.message for record in caplog.records]
        assert any("Worker state loaded" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_load_state_logs_info_on_not_found(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test load_state logs info when no state found."""
        storage = MagicMock()
        storage.get = AsyncMock(return_value=None)
        manager = WorkerStateManager(storage=storage, worker_id="worker-test")

        with caplog.at_level(logging.INFO):
            await manager.load_state()

        log_messages = [record.message for record in caplog.records]
        assert any("No saved state found" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_load_state_logs_error_on_failure(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test load_state logs error on storage failure."""
        storage = MagicMock()
        storage.get = AsyncMock(side_effect=Exception("Timeout"))
        manager = WorkerStateManager(storage=storage, worker_id="worker-01")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(StorageError):
                await manager.load_state()

        log_messages = [record.message for record in caplog.records]
        assert any("Failed to load worker state" in msg for msg in log_messages)


class TestWorkerStateManagerGenerateStateKey:
    """Test WorkerStateManager _generate_state_key method."""

    def test_generate_state_key_format(self) -> None:
        """Test state key has correct format."""
        storage = MagicMock()
        worker_id = "worker-123"
        manager = WorkerStateManager(storage=storage, worker_id=worker_id)

        key = manager._generate_state_key()

        assert key == "worker:state:worker-123"

    def test_generate_state_key_different_ids(self) -> None:
        """Test different worker IDs produce different keys."""
        storage = MagicMock()

        manager1 = WorkerStateManager(storage=storage, worker_id="worker-01")
        manager2 = WorkerStateManager(storage=storage, worker_id="worker-02")

        key1 = manager1._generate_state_key()
        key2 = manager2._generate_state_key()

        assert key1 != key2
        assert key1 == "worker:state:worker-01"
        assert key2 == "worker:state:worker-02"


class TestWorkerStateManagerIntegration:
    """Integration tests for WorkerStateManager."""

    @pytest.mark.asyncio
    async def test_save_and_load_round_trip(self) -> None:
        """Test saving and loading state in round trip."""
        saved_state: dict[str, object] | None = None

        async def mock_set(key: str, value: dict[str, object]) -> None:
            nonlocal saved_state
            saved_state = value

        async def mock_get(key: str) -> dict[str, object] | None:
            return saved_state

        storage = MagicMock()
        storage.set = AsyncMock(side_effect=mock_set)
        storage.get = AsyncMock(side_effect=mock_get)

        manager = WorkerStateManager(storage=storage, worker_id="worker-01")

        # Save state
        original_state = {
            "last_processed_id": "msg-999",
            "windows": {"w1": {"count": 5}, "w2": {"count": 10}},
        }
        await manager.save_state(original_state)

        # Load state
        loaded_state = await manager.load_state()

        assert loaded_state == original_state

    @pytest.mark.asyncio
    async def test_multiple_saves_overwrite(self) -> None:
        """Test multiple saves overwrite previous state."""
        saved_state: dict[str, object] | None = None

        async def mock_set(key: str, value: dict[str, object]) -> None:
            nonlocal saved_state
            saved_state = value

        async def mock_get(key: str) -> dict[str, object] | None:
            return saved_state

        storage = MagicMock()
        storage.set = AsyncMock(side_effect=mock_set)
        storage.get = AsyncMock(side_effect=mock_get)

        manager = WorkerStateManager(storage=storage, worker_id="worker-01")

        # First save
        await manager.save_state({"version": 1})
        state_v1 = await manager.load_state()
        assert state_v1 == {"version": 1}

        # Second save overwrites
        await manager.save_state({"version": 2})
        state_v2 = await manager.load_state()
        assert state_v2 == {"version": 2}


__all__ = ["TestWorkerStateManagerInitialization", "TestWorkerStateManagerSaveState", "TestWorkerStateManagerLoadState", "TestWorkerStateManagerGenerateStateKey", "TestWorkerStateManagerIntegration"]
