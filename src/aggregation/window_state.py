"""Worker state management.

Class:
    WorkerStateManager: Manages worker state persistence.
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
        """Initialize state manager."""
        raise NotImplementedError

    async def save_state(self, state: dict[str, object]) -> None:
        """Save worker state.

        Args:
            state: State dictionary to persist.
        """
        raise NotImplementedError

    async def load_state(self) -> dict[str, object] | None:
        """Load worker state.

        Returns:
            Saved state if exists, None otherwise.
        """
        raise NotImplementedError


__all__ = ["WorkerStateManager"]
