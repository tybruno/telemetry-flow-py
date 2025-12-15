"""Tests for logging formatter update path in setup_logging.

This module tests the branch where an existing StreamHandler without a
formatter gets a formatter added during setup_logging.
"""
import logging
import sys

from src.utils.logging import setup_logging


class TestLoggingFormatterUpdate:
    """Test formatter update on existing handlers."""

    def test_setup_logging_adds_formatter_to_handler_without_formatter(
        self
    ) -> None:
        """Test setup_logging adds formatter to StreamHandler without one.
        
        This test covers the branch where an existing StreamHandler has no
        formatter set, so setup_logging adds one.
        """
        # Create a StreamHandler without a formatter
        handler = logging.StreamHandler(sys.stdout)
        assert handler.formatter is None
        
        # Add handler to root logger
        logging.root.handlers = [handler]
        
        # Call setup_logging - should add formatter to existing handler
        setup_logging(log_level="INFO")
        
        # Verify formatter was added
        assert handler.formatter is not None
        assert "%(asctime)s" in handler.formatter._fmt
        assert "%(levelname)s" in handler.formatter._fmt
        
        # Cleanup
        logging.root.handlers = []
    
    def test_setup_logging_preserves_existing_formatter(self) -> None:
        """Test setup_logging preserves existing formatter on StreamHandler.
        
        When a StreamHandler already has a formatter, setup_logging should
        not replace it.
        """
        # Create a StreamHandler with a custom formatter
        handler = logging.StreamHandler(sys.stdout)
        custom_formatter = logging.Formatter("CUSTOM: %(message)s")
        handler.setFormatter(custom_formatter)
        
        # Add handler to root logger
        logging.root.handlers = [handler]
        
        # Call setup_logging - should preserve existing formatter
        setup_logging(log_level="DEBUG")
        
        # Verify original formatter is preserved
        assert handler.formatter is custom_formatter
        assert handler.formatter._fmt == "CUSTOM: %(message)s"
        
        # Cleanup
        logging.root.handlers = []
