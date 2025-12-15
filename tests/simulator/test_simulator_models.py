"""Tests for simulator models."""

import pytest

from simulator.models import DeviceConfig


class TestDeviceConfig:
    """Test suite for DeviceConfig model."""

    def test_device_config_creation(self) -> None:
        """Test DeviceConfig can be created with all fields."""
        config = DeviceConfig(
            device_id="router-01",
            interfaces=["eth0", "eth1"],
            metrics=["cpu", "memory"],
            interval_seconds=60,
        )

        assert config.device_id == "router-01"
        assert config.interfaces == ["eth0", "eth1"]
        assert config.metrics == ["cpu", "memory"]
        assert config.interval_seconds == 60

    def test_device_config_is_frozen(self) -> None:
        """Test DeviceConfig is immutable."""
        config = DeviceConfig(
            device_id="router-01",
            interfaces=["eth0"],
            metrics=["cpu"],
            interval_seconds=60,
        )

        with pytest.raises(AttributeError):
            config.device_id = "router-02"  # type: ignore[misc]

    def test_device_config_empty_lists(self) -> None:
        """Test DeviceConfig accepts empty lists."""
        config = DeviceConfig(
            device_id="router-01",
            interfaces=[],
            metrics=[],
            interval_seconds=60,
        )

        assert config.interfaces == []
        assert config.metrics == []


__all__: list[str] = []
