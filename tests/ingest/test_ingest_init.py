"""Tests for ingest __init__ module."""

from src.ingest import (
    HealthResponse,
    IngestError,
    IngestRequest,
    IngestResponse,
    IngestService,
    InvalidPayloadError,
    ServiceUnavailableError,
    StreamPublishError,
    create_app,
    main,
    router,
)


class TestIngestInit:
    """Test suite for ingest __init__ module."""

    def test_ingest_service_is_importable(self) -> None:
        """Test IngestService can be imported."""
        assert IngestService is not None

    def test_create_app_is_importable(self) -> None:
        """Test create_app can be imported."""
        assert create_app is not None

    def test_main_is_importable(self) -> None:
        """Test main can be imported."""
        assert main is not None

    def test_router_is_importable(self) -> None:
        """Test router can be imported."""
        assert router is not None

    def test_models_are_importable(self) -> None:
        """Test ingest models can be imported."""
        assert IngestRequest is not None
        assert IngestResponse is not None
        assert HealthResponse is not None

    def test_exceptions_are_importable(self) -> None:
        """Test ingest exceptions can be imported."""
        assert IngestError is not None
        assert InvalidPayloadError is not None
        assert StreamPublishError is not None
        assert ServiceUnavailableError is not None


__all__: list[str] = []
