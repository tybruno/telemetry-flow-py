"""Tests for BaseStorage validation."""

import pytest

from src.storage.base import BaseStorage


class ConcreteStorage(BaseStorage):
    """Concrete storage for testing."""

    async def store(self, key: str, value) -> None:
        """Test implementation."""
        self._validate_key(key)

    async def retrieve(self, key: str):
        """Test implementation."""
        self._validate_key(key)
        return None


class TestBaseStorageValidation:
    """Test BaseStorage validation methods."""

    @pytest.fixture
    def storage(self) -> ConcreteStorage:
        """Create storage instance.

        Returns:
            ConcreteStorage instance.
        """
        return ConcreteStorage()

    async def test_validate_key_empty_raises(
        self,
        storage: ConcreteStorage,
    ) -> None:
        """Test _validate_key raises on empty key.

        Args:
            storage: ConcreteStorage fixture.
        """
        with pytest.raises(ValueError, match="Storage key cannot be empty"):
            await storage.store("", "value")

    async def test_validate_key_whitespace_only_raises(
        self,
        storage: ConcreteStorage,
    ) -> None:
        """Test _validate_key raises on whitespace-only key.

        Args:
            storage: ConcreteStorage fixture.
        """
        with pytest.raises(ValueError, match="Storage key cannot be empty"):
            await storage.store("   ", "value")

    async def test_validate_key_too_long_raises(
        self,
        storage: ConcreteStorage,
    ) -> None:
        """Test _validate_key raises on key > 1024 chars.

        Args:
            storage: ConcreteStorage fixture.
        """
        long_key = "x" * 1025
        
        with pytest.raises(ValueError, match="Storage key too long"):
            await storage.store(long_key, "value")

    async def test_validate_key_max_length_ok(
        self,
        storage: ConcreteStorage,
    ) -> None:
        """Test _validate_key accepts key at max length.

        Args:
            storage: ConcreteStorage fixture.
        """
        max_key = "x" * 1024
        
        # Should not raise
        await storage.store(max_key, "value")

    def test_log_operation(
        self,
        storage: ConcreteStorage,
    ) -> None:
        """Test _log_operation logs correctly.

        Args:
            storage: ConcreteStorage fixture.
        """
        # Should not raise
        storage._log_operation("test", "test_key")


__all__: list[str] = []
