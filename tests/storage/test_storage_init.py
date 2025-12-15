"""Tests for storage __init__ module."""

from src.storage import (
    BaseStorage,
    RedisStore,
    StatePersistenceError,
    StateSnapshot,
    StorageError,
)


class TestStorageInit:
    """Test suite for storage __init__ module."""

    def test_base_storage_is_importable(self) -> None:
        """Test BaseStorage can be imported."""
        assert BaseStorage is not None

    def test_redis_store_is_importable(self) -> None:
        """Test RedisStore can be imported."""
        assert RedisStore is not None

    def test_state_snapshot_is_importable(self) -> None:
        """Test StateSnapshot can be imported."""
        assert StateSnapshot is not None

    def test_storage_error_is_importable(self) -> None:
        """Test StorageError can be imported."""
        assert StorageError is not None

    def test_state_persistence_error_is_importable(self) -> None:
        """Test StatePersistenceError can be imported."""
        assert StatePersistenceError is not None


__all__: list[str] = []
