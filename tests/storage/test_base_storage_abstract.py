"""Tests for BaseStorage abstract methods."""

import pytest

from src.storage.base import BaseStorage


class TestBaseStorageAbstract:
    """Test BaseStorage abstract method behavior."""

    def test_cannot_instantiate_abstract_base_storage(self) -> None:
        """Test cannot instantiate BaseStorage directly."""
        with pytest.raises(TypeError, match="abstract"):
            BaseStorage()


__all__: list[str] = []
