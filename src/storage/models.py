"""Storage infrastructure models.

Classes:
    StateSnapshot: Worker state snapshot.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True, kw_only=True)
class StateSnapshot:
    """Worker state snapshot.

    Attributes:
        worker_id: Worker identifier.
        state_data: State data dictionary.
        timestamp: Snapshot timestamp.
    """

    worker_id: str
    state_data: dict[str, Any]
    timestamp: datetime


__all__ = ["StateSnapshot"]
