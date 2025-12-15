"""Tests for storage exceptions."""

import pytest

from src.core.exceptions import TelemetryError
from src.storage.exceptions import StatePersistenceError, StorageError


class TestStorageExceptions:
    """Test suite for storage exception classes."""

    def test_storage_error_inherits_from_telemetry_error(self) -> None:
        """Test StorageError is subclass of TelemetryError."""
        assert issubclass(StorageError, TelemetryError)

    def test_storage_error_can_be_raised(self) -> None:
        """Test StorageError can be raised with message."""
        with pytest.raises(StorageError, match="test error"):
            raise StorageError("test error")

    def test_state_persistence_error_inherits_from_storage_error(
        self,
    ) -> None:
        """Test StatePersistenceError is subclass of StorageError."""
        assert issubclass(StatePersistenceError, StorageError)

    def test_state_persistence_error_can_be_raised(self) -> None:
        """Test StatePersistenceError can be raised with message."""
        with pytest.raises(StatePersistenceError, match="Persistence failed"):
            raise StatePersistenceError("Persistence failed")

    def test_exceptions_can_be_caught_as_storage_error(self) -> None:
        """Test all exceptions can be caught as StorageError."""
        with pytest.raises(StorageError):
            raise StatePersistenceError("error")


__all__: list[str] = []
