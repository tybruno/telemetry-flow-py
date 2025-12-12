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

from typing import Any


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
        raise NotImplementedError


__all__ = ["ConsoleAlerter"]
