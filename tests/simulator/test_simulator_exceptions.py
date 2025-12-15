"""Tests for simulator exceptions."""

import pytest

from simulator.exceptions import SimulatorError


class TestSimulatorError:
    """Test suite for SimulatorError exception."""

    def test_simulator_error_inherits_from_exception(self) -> None:
        """Test SimulatorError is subclass of Exception."""
        assert issubclass(SimulatorError, Exception)

    def test_simulator_error_can_be_raised(self) -> None:
        """Test SimulatorError can be raised with message."""
        with pytest.raises(SimulatorError, match="test error"):
            raise SimulatorError("test error")

    def test_simulator_error_without_message(self) -> None:
        """Test SimulatorError can be raised without message."""
        with pytest.raises(SimulatorError):
            raise SimulatorError()


__all__: list[str] = []
