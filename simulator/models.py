"""Simulator-specific models.

Classes:
    DeviceConfig: Device configuration.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class DeviceConfig:
    """Device simulator configuration.

    Attributes:
        device_id: Device identifier.
        interfaces: List of interface names.
        metrics: List of metrics to simulate.
        interval_seconds: Simulation interval.
    """

    device_id: str
    interfaces: list[str]
    metrics: list[str]
    interval_seconds: int


__all__ = ["DeviceConfig"]
