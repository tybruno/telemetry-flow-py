"""Core domain models, protocols, and shared abstractions.

Models:
    TelemetryEvent: Core telemetry event data model

Protocols:
    StreamProtocol: Abstract interface for stream operations
    StorageProtocol: Abstract interface for storage operations
    AlerterProtocol: Abstract interface for alert delivery

Configuration:
    BaseConfig: Base configuration with common settings

Exceptions:
    TelemetryError: Base exception for all telemetry errors
    ConfigurationError: Configuration validation errors
    ValidationError: Data validation errors
"""

from src.core.config import BaseConfig
from src.core.exceptions import (
    ConfigurationError,
    TelemetryError,
    ValidationError,
)
from src.core.models import TelemetryEvent
from src.core.protocols import AlerterProtocol, StorageProtocol, StreamProtocol

__all__ = [
    "AlerterProtocol",
    "BaseConfig",
    "ConfigurationError",
    "StorageProtocol",
    "StreamProtocol",
    "TelemetryError",
    "TelemetryEvent",
    "ValidationError",
]
