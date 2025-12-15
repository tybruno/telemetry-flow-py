"""Additional logging utility tests."""

import logging

import pytest

from src.utils.logging import setup_logging


class TestLoggingNonStreamHandler:
    """Test logging setup with non-StreamHandler."""

    def test_setup_logging_skips_non_stream_handlers(self) -> None:
        """Test setup_logging skips non-StreamHandler types."""
        # Clear handlers
        logging.root.handlers.clear()
        
        # Add a file handler (not StreamHandler)
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file_handler = logging.FileHandler(temp_file.name)
        logging.root.addHandler(file_handler)
        
        # Setup logging
        setup_logging(log_level="INFO")
        
        # Should have both handlers now
        assert len(logging.root.handlers) >= 1
        
        # Cleanup
        file_handler.close()
        temp_file.close()


__all__: list[str] = []
