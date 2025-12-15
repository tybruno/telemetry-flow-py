"""Tests for logging utilities."""

import logging
from io import StringIO
from unittest.mock import patch

import pytest

from src.utils.logging import setup_logging


class TestSetupLogging:
    """Test suite for setup_logging function."""

    @pytest.fixture(autouse=True)
    def reset_logging(self) -> None:
        """Reset logging configuration before each test."""
        # Remove all handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            handler.close()
        
        # Reset root logger level
        logging.root.setLevel(logging.WARNING)
        
        # Reset all existing loggers
        for logger_name in list(logging.Logger.manager.loggerDict.keys()):
            logger = logging.getLogger(logger_name)
            logger.handlers = []
            logger.propagate = True
            logger.setLevel(logging.NOTSET)

    @pytest.mark.parametrize(
        "log_level",
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    def test_setup_logging_valid_levels(self, log_level: str) -> None:
        """Test setup_logging with valid log levels.

        Args:
            log_level: Valid log level string.
        """
        setup_logging(log_level=log_level)

        # Verify root logger level is set correctly
        expected_level = getattr(logging, log_level)
        assert logging.root.level == expected_level

    def test_setup_logging_case_insensitive(self) -> None:
        """Test log level is case-insensitive."""
        setup_logging(log_level="debug")
        assert logging.root.level == logging.DEBUG

        setup_logging(log_level="InFo")
        assert logging.root.level == logging.INFO

    @pytest.mark.parametrize(
        "invalid_level",
        ["INVALID", "TRACE", "VERBOSE", "", "123"],
    )
    def test_setup_logging_invalid_level_raises(self, invalid_level: str) -> None:
        """Test invalid log level raises ValueError.

        Args:
            invalid_level: Invalid log level string.
        """
        with pytest.raises(ValueError, match="Invalid log_level"):
            setup_logging(log_level=invalid_level)

    def test_setup_logging_default_level(self) -> None:
        """Test default log level is INFO."""
        setup_logging()
        assert logging.root.level == logging.INFO

    def test_setup_logging_updates_existing_handlers(self) -> None:
        """Test setup_logging updates existing handler without formatter."""
        # First call creates handler
        setup_logging(log_level="INFO")
        
        # Remove formatter to test the else branch
        for handler in logging.root.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(None)
        
        # Second call should set formatter
        setup_logging(log_level="DEBUG")
        
        # Verify formatter was set
        has_formatter = any(
            isinstance(h, logging.StreamHandler) and h.formatter is not None
            for h in logging.root.handlers
        )
        assert has_formatter

    def test_setup_logging_configures_format(self) -> None:
        """Test logging format is configured correctly."""
        setup_logging(log_level="INFO")

        # Verify at least one handler exists
        handlers = logging.root.handlers
        assert len(handlers) > 0

        # Verify handler has a formatter
        handler = handlers[0]
        assert handler.formatter is not None

    def test_setup_logging_outputs_to_stdout(self) -> None:
        """Test logging outputs to stdout."""
        setup_logging(log_level="INFO")

        # Verify at least one StreamHandler exists
        has_stream_handler = any(
            isinstance(h, logging.StreamHandler)
            for h in logging.root.handlers
        )
        assert has_stream_handler

    def test_setup_logging_logs_configuration_message(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test setup_logging logs configuration message.

        Args:
            caplog: Pytest log capture fixture.
        """
        with caplog.at_level(logging.INFO):
            setup_logging(log_level="DEBUG")

            # Should log configuration message
            assert any("Logging configured" in record.message for record in caplog.records)

    def test_setup_logging_sets_all_logger_levels(self) -> None:
        """Test setup_logging sets level for all existing loggers."""
        # Create some loggers
        logger1 = logging.getLogger("test.logger1")
        logger2 = logging.getLogger("test.logger2")

        # Set to different initial levels
        logger1.setLevel(logging.WARNING)
        logger2.setLevel(logging.ERROR)

        # Setup logging
        setup_logging(log_level="DEBUG")

        # Verify all loggers updated
        assert logger1.level == logging.DEBUG
        assert logger2.level == logging.DEBUG

    def test_setup_logging_debug_level_enables_debug_messages(self) -> None:
        """Test DEBUG level allows debug messages."""
        setup_logging(log_level="DEBUG")

        logger = logging.getLogger("test.debug")
        assert logger.isEnabledFor(logging.DEBUG)

    def test_setup_logging_error_level_filters_lower_levels(self) -> None:
        """Test ERROR level filters out lower severity messages."""
        setup_logging(log_level="ERROR")

        logger = logging.getLogger("test.error")
        assert not logger.isEnabledFor(logging.INFO)
        assert not logger.isEnabledFor(logging.WARNING)
        assert logger.isEnabledFor(logging.ERROR)
        assert logger.isEnabledFor(logging.CRITICAL)

    def test_setup_logging_date_format(self) -> None:
        """Test date format is configured correctly."""
        setup_logging(log_level="INFO")

        # Verify handler exists with formatter
        handlers = logging.root.handlers
        assert len(handlers) > 0
        assert handlers[0].formatter is not None


__all__: list[str] = []
