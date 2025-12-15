"""Tests for simulator main entry points."""

from simulator.main import main


class TestSimulatorMain:
    """Test simulator main function."""

    def test_main_exists(self) -> None:
        """Test main function exists and is callable."""
        assert callable(main)


__all__: list[str] = []
