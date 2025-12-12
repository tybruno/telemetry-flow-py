"""Base exception hierarchy for the telemetry system.

This module defines the root exception classes that all service-specific
exceptions inherit from. This enables both fine-grained and broad
exception handling across the system.

Classes:
    TelemetryError: Root exception for all telemetry-related errors.
    ConfigurationError: Configuration-related errors.
    ValidationError: Data validation errors.

Example:
    Handling exceptions at different levels::
    
        try:
            await service.process()
        except ConfigurationError as e:
            # Handle configuration issues
            _log.error("Config error: %s", e)
        except TelemetryError as e:
            # Catch-all for any telemetry error
            _log.error("System error: %s", e)
"""


class TelemetryError(Exception):
    """Root exception for all telemetry system errors.
    
    All custom exceptions in the telemetry system inherit from this
    base class. This enables broad exception handling when needed
    while still allowing fine-grained error handling.
    
    Example:
        Catching all telemetry errors::
        
            try:
                await process_telemetry()
            except TelemetryError as e:
                _log.error("Telemetry system error: %s", e)
    """


class ConfigurationError(TelemetryError):
    """Configuration-related errors across all services.
    
    Raised when configuration is invalid, missing, or cannot be loaded.
    This applies to environment variables, YAML files, and runtime config.
    
    Example:
        Invalid configuration::
        
            if not config.redis_url:
                raise ConfigurationError("Redis URL is required")
    """


class ValidationError(TelemetryError):
    """Data validation errors.
    
    Raised when input data fails validation checks. Used for validating
    telemetry events, API payloads, and configuration values.
    
    Example:
        Invalid telemetry data::
        
            if event.metric_value < 0:
                raise ValidationError(
                    f"Metric value cannot be negative: {event.metric_value}"
                )
    """


__all__ = [
    "TelemetryError",
    "ConfigurationError",
    "ValidationError",
]
