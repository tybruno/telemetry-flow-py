"""Tests for console alerter implementation."""

import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.alerts.console import ConsoleAlerter
from src.alerts.exceptions import AlertDeliveryError


class TestConsoleAlerter:
    """Test suite for ConsoleAlerter class."""

    @pytest.fixture
    def alerter(self) -> ConsoleAlerter:
        """Create alerter instance for testing.

        Returns:
            ConsoleAlerter instance.
        """
        console_alerter = ConsoleAlerter()
        return console_alerter

    @pytest.fixture
    def valid_context(self) -> dict[str, Any]:
        """Create valid alert context.

        Returns:
            Context dictionary with sample data.
        """
        context_data: dict[str, Any] = {
            "device_id": "router-01",
            "interface": "eth0",
            "value": 95.5,
            "threshold": 90.0,
        }
        return context_data

    @pytest.mark.parametrize(
        "severity",
        ["low", "medium", "high", "critical", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
    )
    async def test_send_alert_valid_severity(
        self,
        alerter: ConsoleAlerter,
        valid_context: dict[str, Any],
        severity: str,
    ) -> None:
        """Test send_alert with valid severity levels.

        Args:
            alerter: ConsoleAlerter fixture.
            valid_context: Valid context fixture.
            severity: Severity level to test.
        """
        with patch("builtins.print") as mock_print:
            await alerter.send_alert(
                severity=severity,
                message="Test alert",
                context=valid_context,
            )

            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert severity.upper() in call_args
            assert "Test alert" in call_args

    async def test_send_alert_formats_output_correctly(
        self,
        alerter: ConsoleAlerter,
        valid_context: dict[str, Any],
    ) -> None:
        """Test alert formatting includes severity, message, context.

        Args:
            alerter: ConsoleAlerter fixture.
            valid_context: Valid context fixture.
        """
        with patch("builtins.print") as mock_print:
            await alerter.send_alert(
                severity="high",
                message="CPU threshold exceeded",
                context=valid_context,
            )

            output = mock_print.call_args[0][0]
            assert "[HIGH]" in output
            assert "CPU threshold exceeded" in output
            assert "device_id=router-01" in output
            assert "interface=eth0" in output
            assert "value=95.5" in output
            assert "threshold=90.0" in output

    async def test_send_alert_empty_context(
        self,
        alerter: ConsoleAlerter,
    ) -> None:
        """Test alert with empty context dictionary.

        Args:
            alerter: ConsoleAlerter fixture.
        """
        with patch("builtins.print") as mock_print:
            await alerter.send_alert(
                severity="critical",
                message="Service down",
                context={},
            )

            output = mock_print.call_args[0][0]
            assert "[CRITICAL] Service down" == output

    @pytest.mark.parametrize(
        "invalid_severity",
        ["invalid", "warn", "error", "info", "debug", ""],
    )
    async def test_send_alert_invalid_severity_raises(
        self,
        alerter: ConsoleAlerter,
        valid_context: dict[str, Any],
        invalid_severity: str,
    ) -> None:
        """Test send_alert raises ValueError for invalid severity.

        Args:
            alerter: ConsoleAlerter fixture.
            valid_context: Valid context fixture.
            invalid_severity: Invalid severity level.
        """
        with pytest.raises(ValueError, match="Invalid severity"):
            await alerter.send_alert(
                severity=invalid_severity,
                message="Test message",
                context=valid_context,
            )

    @pytest.mark.parametrize(
        "invalid_message",
        ["", "   ", "\t", "\n"],
    )
    async def test_send_alert_empty_message_raises(
        self,
        alerter: ConsoleAlerter,
        valid_context: dict[str, Any],
        invalid_message: str,
    ) -> None:
        """Test send_alert raises ValueError for empty message.

        Args:
            alerter: ConsoleAlerter fixture.
            valid_context: Valid context fixture.
            invalid_message: Invalid message string.
        """
        with pytest.raises(ValueError, match="Alert message cannot be empty"):
            await alerter.send_alert(
                severity="high",
                message=invalid_message,
                context=valid_context,
            )

    async def test_send_alert_logs_warning(
        self,
        alerter: ConsoleAlerter,
        valid_context: dict[str, Any],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test send_alert logs alert as warning.

        Args:
            alerter: ConsoleAlerter fixture.
            valid_context: Valid context fixture.
            caplog: Pytest log capture fixture.
        """
        with patch("builtins.print"):
            with caplog.at_level(logging.WARNING):
                await alerter.send_alert(
                    severity="critical",
                    message="Test alert",
                    context=valid_context,
                )

                assert len(caplog.records) == 1
                assert caplog.records[0].levelname == "WARNING"
                assert "ALERT:" in caplog.records[0].message

    async def test_send_alert_format_exception_raises_delivery_error(
        self,
        alerter: ConsoleAlerter,
    ) -> None:
        """Test formatting exception raises AlertDeliveryError.

        Args:
            alerter: ConsoleAlerter fixture.
        """
        # Create mock that raises when str() is called on it
        bad_value = MagicMock()
        bad_value.__str__ = MagicMock(side_effect=Exception("boom"))
        bad_context: dict[str, Any] = {"key": bad_value}

        with pytest.raises(AlertDeliveryError, match="Failed to send alert"):
            await alerter.send_alert(
                severity="high",
                message="Test",
                context=bad_context,
            )

    async def test_validate_severity_case_insensitive(
        self,
        alerter: ConsoleAlerter,
        valid_context: dict[str, Any],
    ) -> None:
        """Test severity validation is case-insensitive.

        Args:
            alerter: ConsoleAlerter fixture.
            valid_context: Valid context fixture.
        """
        with patch("builtins.print"):
            # Should not raise
            await alerter.send_alert(
                severity="CrItIcAl",
                message="Mixed case severity",
                context=valid_context,
            )

    async def test_format_alert_with_multiple_context_items(
        self,
        alerter: ConsoleAlerter,
    ) -> None:
        """Test formatting with multiple context items.

        Args:
            alerter: ConsoleAlerter fixture.
        """
        context: dict[str, Any] = {
            "item1": "value1",
            "item2": 42,
            "item3": 3.14,
        }

        with patch("builtins.print") as mock_print:
            await alerter.send_alert(
                severity="medium",
                message="Multiple items",
                context=context,
            )

            output = mock_print.call_args[0][0]
            assert "item1=value1" in output
            assert "item2=42" in output
            assert "item3=3.14" in output

    def test_alerter_uses_slots(self) -> None:
        """Test ConsoleAlerter uses __slots__ for memory efficiency."""
        alerter = ConsoleAlerter()
        slots_defined = hasattr(ConsoleAlerter, "__slots__")
        assert slots_defined

        with pytest.raises(AttributeError):
            alerter.arbitrary_attribute = "should fail"  # type: ignore[attr-defined]


__all__: list[str] = []
