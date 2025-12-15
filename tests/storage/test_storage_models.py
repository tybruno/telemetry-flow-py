"""Tests for storage models."""

from datetime import datetime, timezone

import pytest

from src.storage.models import StateSnapshot


class TestStateSnapshot:
    """Test suite for StateSnapshot model."""

    def test_state_snapshot_creation(self) -> None:
        """Test StateSnapshot can be created with all fields."""
        timestamp = datetime(2025, 12, 15, 10, 0, 0, tzinfo=timezone.utc)

        snapshot = StateSnapshot(
            worker_id="worker-01",
            state_data={"last_offset": "1234567890-0", "windows": {}},
            timestamp=timestamp,
        )

        assert snapshot.worker_id == "worker-01"
        assert snapshot.state_data == {"last_offset": "1234567890-0", "windows": {}}
        assert snapshot.timestamp == timestamp

    def test_state_snapshot_is_frozen(self) -> None:
        """Test StateSnapshot is immutable."""
        snapshot = StateSnapshot(
            worker_id="worker-01",
            state_data={},
            timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(AttributeError):
            snapshot.worker_id = "worker-02"  # type: ignore[misc]

    def test_state_snapshot_empty_state_data(self) -> None:
        """Test StateSnapshot accepts empty state_data."""
        snapshot = StateSnapshot(
            worker_id="worker-01",
            state_data={},
            timestamp=datetime.now(timezone.utc),
        )

        assert snapshot.state_data == {}


__all__: list[str] = []
