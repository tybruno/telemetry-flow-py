"""Console alerter implementation.

This module provides a simple console-based alerter that outputs alerts
to stdout for visibility during development and debugging.

Classes:
    ConsoleAlerter: Console output alerter implementation.

Example:
    Basic alert usage::

        from alerts import ConsoleAlerter

        alerter = ConsoleAlerter()
        await alerter.send_alert(
            severity="high",
            message="CPU threshold exceeded",
            context={
                "device_id": "router-01",
                "value": 95.5,
                "threshold": 90.0
            }
        )
"""

import logging as _log
from typing import Any

from src.alerts.exceptions import AlertDeliveryError


class ConsoleAlerter:
    """Console alerter implementation of AlerterProtocol.

    Outputs alerts to console/logs for visibility during development
    and debugging. In production, this would typically be replaced with
    email, PagerDuty, Slack, or other notification systems.

    Attributes:
        This class has no instance attributes (uses __slots__ = ()).

    Example:
        Using the console alerter::

            alerter = ConsoleAlerter()

            await alerter.send_alert(
                severity="critical",
                message="Device offline",
                context={"device_id": "router-01"}
            )
            # Output: [CRITICAL] Device offline | device_id=router-01
    """

    __slots__ = ()

    async def send_alert(
        self,
        *,
        severity: str,
        message: str,
        context: dict[str, Any],
    ) -> None:
        """Send alert to console output.

        Args:
            severity: Alert severity level (low, medium, high, critical).
            message: Human-readable alert message.
            context: Additional context data for the alert (device_id,
                metric values, thresholds, etc.).

        Raises:
            ValueError: If severity is invalid or message is empty.
            AlertError: If alert formatting or output fails.

        Example:
            await alerter.send_alert(
                severity="high",
                message="Bandwidth threshold exceeded",
                context={
                    "device_id": "router-01",
                    "interface": "eth0",
                    "value": 95.5,
                    "threshold": 90.0
                }
            )
        """
        self._validate_severity(severity)
        self._validate_message(message)

        try:
            formatted_alert = self._format_alert(severity, message, context)
            print(formatted_alert)
            _log.warning("ALERT: %s", formatted_alert)
        except Exception as e:
            error_message = "Failed to send alert: %s"
            _log.error(error_message, str(e))
            raise AlertDeliveryError(error_message % str(e)) from e

    def _validate_severity(self, severity: str) -> None:
        """Validate severity level.

        Args:
            severity: Severity level to validate.

        Raises:
            ValueError: If severity is invalid.
        """
        valid_severities = {"low", "medium", "high", "critical"}
        if severity.casefold() not in valid_severities:
            error_message = "Invalid severity: %s. Must be one of %s"
            _log.error(error_message, severity, valid_severities)
            raise ValueError(error_message % (severity, valid_severities)) from None

    def _validate_message(self, message: str) -> None:
        """Validate alert message.

        Args:
            message: Message to validate.

        Raises:
            ValueError: If message is empty.
        """
        if not message or not message.strip():
            error_message = "Alert message cannot be empty"
            _log.error(error_message)
            raise ValueError(error_message) from None

    def _format_alert(
        self,
        severity: str,
        message: str,
        context: dict[str, Any],
    ) -> str:
        """Format alert for console output.

        Args:
            severity: Severity level.
            message: Alert message.
            context: Context dictionary.

        Returns:
            Formatted alert string.
        """
        severity_upper = severity.upper()
        context_str = " | ".join(f"{k}={v}" for k, v in context.items())
        formatted_message = f"[{severity_upper}] {message}"

        if context_str:
            formatted_message = f"{formatted_message} | {context_str}"

        return formatted_message


__all__ = ["ConsoleAlerter"]
