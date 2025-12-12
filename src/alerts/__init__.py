"""Alert infrastructure for anomaly notifications.

Classes:
    ConsoleAlerter: Console-based alert delivery implementation
    Alert: Generic alert model
    AlertSeverity: Alert severity levels

Exceptions:
    AlertError: Base exception for alert errors
    AlertDeliveryError: Alert delivery failure
"""

from src.alerts.console import ConsoleAlerter
from src.alerts.exceptions import AlertDeliveryError, AlertError
from src.alerts.models import Alert, AlertSeverity

__all__ = [
    "Alert",
    "AlertDeliveryError",
    "AlertError",
    "AlertSeverity",
    "ConsoleAlerter",
]
