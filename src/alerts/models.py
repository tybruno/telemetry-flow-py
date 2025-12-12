"""Alert infrastructure models.

Classes:
    AlertSeverity: Alert severity levels.
    Alert: Generic alert model.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True, kw_only=True)
class Alert:
    """Generic alert model.

    Attributes:
        severity: Alert severity level.
        message: Human-readable alert message.
        source: Alert source identifier.
        metadata: Additional context data.
        timestamp: Alert timestamp.
    """

    severity: AlertSeverity
    message: str
    source: str
    metadata: dict[str, Any]
    timestamp: datetime


__all__ = ["Alert", "AlertSeverity"]
