"""Tests for ingest exceptions."""

import pytest

from src.core.exceptions import TelemetryError
from src.ingest.exceptions import (
    IngestError,
    InvalidPayloadError,
    ServiceUnavailableError,
    StreamPublishError,
)


class TestIngestExceptions:
    """Test suite for ingest exception classes."""

    def test_ingest_error_inherits_from_telemetry_error(self) -> None:
        """Test IngestError is subclass of TelemetryError."""
        assert issubclass(IngestError, TelemetryError)

    def test_ingest_error_can_be_raised(self) -> None:
        """Test IngestError can be raised with message."""
        with pytest.raises(IngestError, match="test error"):
            raise IngestError("test error")

    def test_invalid_payload_error_inherits_from_ingest_error(self) -> None:
        """Test InvalidPayloadError is subclass of IngestError."""
        assert issubclass(InvalidPayloadError, IngestError)

    def test_invalid_payload_error_can_be_raised(self) -> None:
        """Test InvalidPayloadError can be raised with message."""
        with pytest.raises(InvalidPayloadError, match="Invalid payload"):
            raise InvalidPayloadError("Invalid payload")

    def test_stream_publish_error_inherits_from_ingest_error(self) -> None:
        """Test StreamPublishError is subclass of IngestError."""
        assert issubclass(StreamPublishError, IngestError)

    def test_stream_publish_error_can_be_raised(self) -> None:
        """Test StreamPublishError can be raised with message."""
        with pytest.raises(StreamPublishError, match="Publish failed"):
            raise StreamPublishError("Publish failed")

    def test_service_unavailable_error_inherits_from_ingest_error(
        self,
    ) -> None:
        """Test ServiceUnavailableError is subclass of IngestError."""
        assert issubclass(ServiceUnavailableError, IngestError)

    def test_service_unavailable_error_can_be_raised(self) -> None:
        """Test ServiceUnavailableError can be raised with message."""
        with pytest.raises(ServiceUnavailableError, match="Service down"):
            raise ServiceUnavailableError("Service down")

    def test_exceptions_can_be_caught_as_ingest_error(self) -> None:
        """Test all exceptions can be caught as IngestError."""
        for exc_class in [
            InvalidPayloadError,
            StreamPublishError,
            ServiceUnavailableError,
        ]:
            with pytest.raises(IngestError):
                raise exc_class("error")


__all__: list[str] = []
