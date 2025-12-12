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


from src.core.protocols import StorageProtocol


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
        raise NotImplementedError

    async def save_state(self, state: dict[str, object]) -> None:
        """Save worker state to persistent storage.

        Args:
            state: State dictionary to persist. Typically contains
                last processed message ID and window states.

        Raises:
            StorageError: If state persistence fails.
            ValueError: If state dictionary is invalid.
        """
        raise NotImplementedError

    async def load_state(self) -> dict[str, object] | None:
        """Load worker state from persistent storage.

        Returns:
            Saved state dictionary if exists, None if no state found.
            State typically contains last processed message ID and
            window states for recovery.

        Raises:
            StorageError: If state retrieval fails.
        """
        raise NotImplementedError


__all__ = ["WorkerStateManager"]
