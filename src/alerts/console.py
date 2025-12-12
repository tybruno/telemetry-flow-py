"""Console alerter implementation.

Class:
    ConsoleAlerter: Console output alerter.
"""

import logging
from typing import Any

_log = logging.getLogger(__name__)


class ConsoleAlerter:
    """Console alerter implementation of AlerterProtocol.

    Outputs alerts to console/logs for visibility.
    """

    __slots__ = ()

    async def send_alert(
        self,
        *,
        severity: str,
        message: str,
        context: dict[str, Any],
    ) -> None:
        """Send alert to console.

        Args:
            severity: Alert severity.
            message: Alert message.
            context: Alert context data.
        """
        raise NotImplementedError


__all__ = ["ConsoleAlerter"]
