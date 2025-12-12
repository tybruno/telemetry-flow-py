"""Telemetry processor worker service for stream processing.

Worker:
    TelemetryWorker: Main processing worker orchestrator

Models:
    TelemetryWindowKey: Window identification model
    TelemetryMetricIdentifier: Metric identifier model

Configuration:
    ProcessorConfig: Processor configuration settings

Exceptions:
    ProcessorError: Base exception for processor errors
    OrchestrationError: Worker orchestration failures
    StateRecoveryError: State recovery failures
    TelemetryProcessingError: Processing errors
"""

from src.processor.config import ProcessorConfig
from src.processor.exceptions import (
    OrchestrationError,
    ProcessorError,
    StateRecoveryError,
    TelemetryProcessingError,
)
from src.processor.main import main
from src.processor.models import TelemetryMetricIdentifier, TelemetryWindowKey
from src.processor.worker import TelemetryWorker

__all__ = [
    "OrchestrationError",
    "ProcessorConfig",
    "ProcessorError",
    "StateRecoveryError",
    "TelemetryMetricIdentifier",
    "TelemetryProcessingError",
    "TelemetryWindowKey",
    "TelemetryWorker",
    "main",
]
