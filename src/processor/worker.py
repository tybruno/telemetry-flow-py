"""Telemetry processor worker orchestration.

Class:
    TelemetryWorker: Main worker for processing telemetry streams.
"""

import logging

from src.core.protocols import AlerterProtocol, StorageProtocol, StreamProtocol

_log = logging.getLogger(__name__)


class TelemetryWorker:
    """Main worker for processing telemetry event streams.

    Orchestrates stream consumption, aggregation, anomaly detection,
    and state management. All dependencies injected via protocols.

    Attributes:
        _consumer: Stream consumer implementation.
        _storage: State storage implementation.
        _alerter: Alert delivery implementation.
    """

    __slots__ = ("_consumer", "_storage", "_alerter", "_running")

    _consumer: StreamProtocol
    _storage: StorageProtocol
    _alerter: AlerterProtocol
    _running: bool

    def __init__(
        self,
        *,
        consumer: StreamProtocol,
        storage: StorageProtocol,
        alerter: AlerterProtocol,
    ) -> None:
        """Initialize worker with injected dependencies."""
        raise NotImplementedError

    async def start(self) -> None:
        """Start processing telemetry events."""
        raise NotImplementedError

    async def stop(self) -> None:
        """Stop processing gracefully."""
        raise NotImplementedError


__all__ = ["TelemetryWorker"]
