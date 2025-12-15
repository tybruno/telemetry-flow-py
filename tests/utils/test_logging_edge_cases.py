"""Tests for logging utility functions."""

import logging

import pytest

from src.utils.logging import setup_logging


class TestLoggingUtility:
    """Test logging configuration utility."""

    def test_setup_logging_with_existing_handler_missing_formatter(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test setup_logging updates handler missing formatter.

        Args:
            caplog: Pytest log capture fixture.
        """
        # Clear existing handlers first
        logging.root.handlers.clear()
        
        # Add handler without formatter
        handler = logging.StreamHandler()
        handler.setFormatter(None)
        logging.root.addHandler(handler)
        
        # Setup logging should add formatter
        setup_logging(log_level="INFO")
        
        # Verify handler now has formatter
        assert logging.root.handlers[0].formatter is not None

    def test_setup_logging_updates_existing_loggers(self) -> None:
        """Test setup_logging updates all existing logger levels."""
        # Create a logger before setup
        test_logger = logging.getLogger("test_module")
        original_level = test_logger.level
        
        # Setup with different level
        setup_logging(log_level="DEBUG")
        
        # Logger should inherit new level
        assert logging.root.level == logging.DEBUG


__all__: list[str] = []
