"""Worker state management for processor recovery.

This module provides state persistence and recovery functionality for
processor workers, enabling graceful recovery from failures.

Classes:
    WorkerStateManager: Manages worker state persistence and recovery.

Example:
    Basic state management usage::

        from aggregation import WorkerStateManager
        from storage import RedisStore

        storage = RedisStore(url="redis://localhost")
        manager = WorkerStateManager(
            storage=storage,
            worker_id="worker-01"
        )

        # Save state
        await manager.save_state({
            "last_processed_id": "msg-12345",
            "windows": {...}
        })

        # Recover state
        state = await manager.load_state()
        if state:
            last_id = state["last_processed_id"]
"""

import logging as _log

from src.core.protocols import StorageProtocol
from src.storage.exceptions import StorageError


class WorkerStateManager:
    """Manages worker state persistence and recovery.

    Handles saving and loading worker state for recovery scenarios.

    Attributes:
        _storage: Storage protocol implementation.
        _worker_id: Unique worker identifier.
    """

    __slots__ = ("_storage", "_worker_id")

    _storage: StorageProtocol
    _worker_id: str

    def __init__(
        self,
        *,
        storage: StorageProtocol,
        worker_id: str,
    ) -> None:
        """Initialize state manager.

        Args:
            storage: Storage protocol implementation for persistence.
            worker_id: Unique identifier for this worker instance.

        Raises:
            ValueError: If worker_id is empty or invalid.
        """
        if not worker_id or not worker_id.strip():
            error_message = "Worker ID cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        self._storage = storage
        self._worker_id = worker_id
        _log.info("Worker state manager initialized: worker_id=%s", worker_id)

    async def save_state(self, state: dict[str, object]) -> None:
        """Save worker state to persistent storage.

        Args:
            state: State dictionary to persist. Typically contains
                last processed message ID and window states.

        Raises:
            StorageError: If state persistence fails.
            ValueError: If state dictionary is invalid.
        """
        if not state:
            error_message = "State cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

        state_key = self._generate_state_key()

        try:
            await self._storage.set(state_key, state)
            _log.debug("Worker state saved: worker_id=%s", self._worker_id)
        except Exception as e:
            error_message = "Failed to save worker state: %s"
            _log.error(error_message, str(e))
            raise StorageError(error_message % str(e)) from e

    async def load_state(self) -> dict[str, object] | None:
        """Load worker state from persistent storage.

        Returns:
            Saved state dictionary if exists, None if no state found.
            State typically contains last processed message ID and
            window states for recovery.

        Raises:
            StorageError: If state retrieval fails.
        """
        state_key = self._generate_state_key()

        try:
            state: dict[str, object] | None = await self._storage.get(state_key)
            if state:
                _log.info("Worker state loaded: worker_id=%s", self._worker_id)
            else:
                _log.info("No saved state found: worker_id=%s", self._worker_id)
            return state
        except Exception as e:
            error_message = "Failed to load worker state: %s"
            _log.error(error_message, str(e))
            raise StorageError(error_message % str(e)) from e

    def _generate_state_key(self) -> str:
        """Generate storage key for worker state.

        Returns:
            Storage key for this worker's state.
        """
        state_key = f"worker:state:{self._worker_id}"
        return state_key


__all__ = ["WorkerStateManager"]
