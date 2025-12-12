"""Storage infrastructure exceptions.

Classes:
    StorageError: Base storage exception.
    StatePersistenceError: State persistence failures.
"""

from src.core.exceptions import TelemetryError


class StorageError(TelemetryError):
    """Base exception for storage operations."""


class StatePersistenceError(StorageError):
    """Failed to persist state."""


__all__ = ["StorageError", "StatePersistenceError"]
