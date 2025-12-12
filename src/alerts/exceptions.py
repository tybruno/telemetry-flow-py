"""Alert infrastructure exceptions.

Classes:
    AlertError: Base alert exception.
    AlertDeliveryError: Alert delivery failures.
"""

from src.core.exceptions import TelemetryError


class AlertError(TelemetryError):
    """Base exception for alert operations."""


class AlertDeliveryError(AlertError):
    """Failed to deliver alert."""


__all__ = ["AlertError", "AlertDeliveryError"]
