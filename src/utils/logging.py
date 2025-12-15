"""Structured logging configuration.

This module provides centralized logging setup for consistent log
formatting and level configuration across all services.

Classes:
    None.

Functions:
    setup_logging: Configure structured logging for the application.

Example:
    Setting up logging at application startup::

        from utils import setup_logging

        # Configure for development
        setup_logging(log_level="DEBUG")

        # Configure for production
        setup_logging(log_level="INFO")

        import logging
        _log = logging.getLogger(__name__)
        _log.info("Application started")
"""

import logging
import sys


def setup_logging(*, log_level: str = "INFO") -> None:
    """Configure structured logging for the application.

    Sets up logging with consistent formatting, level configuration,
    and output destinations (console, files, etc.).

    Args:
        log_level: Logging level as string. Must be one of:
            DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO).

    Raises:
        ValueError: If log_level is invalid or not recognized.

    Example:
        Basic logging setup::

            setup_logging(log_level="INFO")

            import logging
            _log = logging.getLogger(__name__)
            _log.info("Service started")
            _log.warning("High CPU detected")
    """
    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    normalized_level = log_level.upper()

    if normalized_level not in valid_levels:
        error_message = "Invalid log_level: %s. Must be one of: %s"
        raise ValueError(error_message % (log_level, ", ".join(valid_levels))) from None

    # Get numeric level
    numeric_level = getattr(logging, normalized_level)

    # Set root logger level
    logging.root.setLevel(numeric_level)

    # Create or update handler
    if not logging.root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)
    else:
        # Update existing handlers
        for handler in logging.root.handlers:
            if isinstance(handler, logging.StreamHandler):
                if not handler.formatter:
                    formatter = logging.Formatter(
                        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                    )
                    handler.setFormatter(formatter)

    # Set level for all existing loggers
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)

    logging.info("Logging configured at level=%s", normalized_level)


__all__ = ["setup_logging"]
