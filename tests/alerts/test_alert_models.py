"""Tests for alert models."""

from datetime import datetime, timezone
from typing import Any

import pytest

from src.alerts.models import Alert, AlertSeverity


class TestAlertSeverity:
    """Test suite for AlertSeverity enum."""

    def test_severity_levels_exist(self) -> None:
        """Test all severity levels are defined."""
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.MEDIUM.value == "medium"
        assert AlertSeverity.HIGH.value == "high"
        assert AlertSeverity.CRITICAL.value == "critical"

    def test_severity_enum_members(self) -> None:
        """Test severity enum has expected members."""
        severities = {s.value for s in AlertSeverity}
        expected_severities = {"low", "medium", "high", "critical"}
        assert severities == expected_severities


class TestAlert:
    """Test suite for Alert dataclass."""

    @pytest.fixture
    def sample_timestamp(self) -> datetime:
        """Create sample timestamp.

        Returns:
            Datetime instance.
        """
        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        return timestamp

    @pytest.fixture
    def sample_metadata(self) -> dict[str, Any]:
        """Create sample metadata.

        Returns:
            Metadata dictionary.
        """
        metadata: dict[str, Any] = {
            "device_id": "router-01",
            "interface": "eth0",
            "value": 95.5,
        }
        return metadata

    def test_alert_creation(
        self,
        sample_timestamp: datetime,
        sample_metadata: dict[str, Any],
    ) -> None:
        """Test Alert dataclass creation.

        Args:
            sample_timestamp: Sample timestamp fixture.
            sample_metadata: Sample metadata fixture.
        """
        alert = Alert(
            severity=AlertSeverity.HIGH,
            message="CPU threshold exceeded",
            source="monitoring-system",
            metadata=sample_metadata,
            timestamp=sample_timestamp,
        )

        assert alert.severity == AlertSeverity.HIGH
        assert alert.message == "CPU threshold exceeded"
        assert alert.source == "monitoring-system"
        assert alert.metadata == sample_metadata
        assert alert.timestamp == sample_timestamp

    def test_alert_is_frozen(
        self,
        sample_timestamp: datetime,
        sample_metadata: dict[str, Any],
    ) -> None:
        """Test Alert dataclass is immutable (frozen).

        Args:
            sample_timestamp: Sample timestamp fixture.
            sample_metadata: Sample metadata fixture.
        """
        alert = Alert(
            severity=AlertSeverity.LOW,
            message="Test",
            source="test",
            metadata=sample_metadata,
            timestamp=sample_timestamp,
        )

        with pytest.raises(Exception):
            alert.severity = AlertSeverity.CRITICAL  # type: ignore[misc]

    def test_alert_uses_slots(self) -> None:
        """Test Alert uses __slots__ for memory efficiency."""
        slots_defined = hasattr(Alert, "__slots__")
        assert slots_defined

    def test_alert_requires_keyword_arguments(
        self,
        sample_timestamp: datetime,
        sample_metadata: dict[str, Any],
    ) -> None:
        """Test Alert requires keyword-only arguments.

        Args:
            sample_timestamp: Sample timestamp fixture.
            sample_metadata: Sample metadata fixture.
        """
        # This should work (keyword arguments)
        alert = Alert(
            severity=AlertSeverity.MEDIUM,
            message="Test",
            source="test",
            metadata=sample_metadata,
            timestamp=sample_timestamp,
        )
        assert alert.severity == AlertSeverity.MEDIUM

        # Positional arguments should fail
        with pytest.raises(TypeError):
            Alert(  # type: ignore[misc]
                AlertSeverity.MEDIUM,
                "Test",
                "test",
                sample_metadata,
                sample_timestamp,
            )

    @pytest.mark.parametrize(
        "severity",
        [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH, AlertSeverity.CRITICAL],
    )
    def test_alert_with_all_severities(
        self,
        severity: AlertSeverity,
        sample_timestamp: datetime,
        sample_metadata: dict[str, Any],
    ) -> None:
        """Test Alert can be created with all severity levels.

        Args:
            severity: Severity level to test.
            sample_timestamp: Sample timestamp fixture.
            sample_metadata: Sample metadata fixture.
        """
        alert = Alert(
            severity=severity,
            message=f"{severity.value} alert",
            source="test",
            metadata=sample_metadata,
            timestamp=sample_timestamp,
        )
        assert alert.severity == severity

    def test_alert_equality(
        self,
        sample_timestamp: datetime,
        sample_metadata: dict[str, Any],
    ) -> None:
        """Test Alert equality comparison.

        Args:
            sample_timestamp: Sample timestamp fixture.
            sample_metadata: Sample metadata fixture.
        """
        alert1 = Alert(
            severity=AlertSeverity.HIGH,
            message="Test",
            source="test",
            metadata=sample_metadata,
            timestamp=sample_timestamp,
        )

        alert2 = Alert(
            severity=AlertSeverity.HIGH,
            message="Test",
            source="test",
            metadata=sample_metadata,
            timestamp=sample_timestamp,
        )

        assert alert1 == alert2

    def test_alert_metadata_can_be_empty(
        self,
        sample_timestamp: datetime,
    ) -> None:
        """Test Alert accepts empty metadata.

        Args:
            sample_timestamp: Sample timestamp fixture.
        """
        alert = Alert(
            severity=AlertSeverity.LOW,
            message="No metadata",
            source="test",
            metadata={},
            timestamp=sample_timestamp,
        )
        assert alert.metadata == {}


__all__: list[str] = []
