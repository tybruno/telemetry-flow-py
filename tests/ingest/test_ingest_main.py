"""Tests for ingest service main module.

This module contains comprehensive tests for the ingest service
application entry point, including app creation, lifespan management,
and main execution.
"""

import importlib
import logging
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI

# Import the module directly using importlib to avoid naming collision
ingest_main = importlib.import_module("src.ingest.main")


class TestCreateApp:
    """Test create_app function."""

    def test_create_app_returns_fastapi_instance(self) -> None:
        """Test create_app returns FastAPI instance."""
        mock_router = MagicMock()
        with patch.object(ingest_main, "router", mock_router):
            app = ingest_main.create_app()

            assert isinstance(app, FastAPI)
            assert app.title == "Telemetry Ingest Service"
            assert app.version == "0.1.0"

    def test_create_app_includes_router(self) -> None:
        """Test create_app includes API router."""
        app = ingest_main.create_app()

        # Check that the router has been included
        # FastAPI includes routes from router when app.include_router() is called
        has_routes = len(app.routes) > 0
        assert has_routes

    def test_create_app_has_cors_middleware(self) -> None:
        """Test create_app configures CORS middleware."""
        mock_router = MagicMock()
        with patch.object(ingest_main, "router", mock_router):
            app = ingest_main.create_app()

            # Check middleware is present
            has_cors = any(
                "CORSMiddleware" in str(middleware)
                for middleware in app.user_middleware
            )
            assert has_cors

    def test_create_app_has_docs_urls(self) -> None:
        """Test create_app configures documentation URLs."""
        mock_router = MagicMock()
        with patch.object(ingest_main, "router", mock_router):
            app = ingest_main.create_app()

            assert app.docs_url == "/docs"
            assert app.redoc_url == "/redoc"

    def test_create_app_logs_info(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test create_app logs application creation."""
        mock_router = MagicMock()
        with patch.object(ingest_main, "router", mock_router):
            with caplog.at_level(logging.INFO):
                ingest_main.create_app()

            log_messages = [record.message for record in caplog.records]
            assert any("FastAPI application created" in msg for msg in log_messages)


class TestLifespan:
    """Test lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_startup_initializes_stream(
        self,
    ) -> None:
        """Test lifespan initializes Redis stream on startup."""
        mock_stream = MagicMock()
        mock_stream.close = AsyncMock()
        mock_stream_class = MagicMock(return_value=mock_stream)

        mock_partitioner = MagicMock()
        mock_partitioner_class = MagicMock(return_value=mock_partitioner)

        mock_init_service = MagicMock()

        with patch.object(ingest_main, "RedisStream", mock_stream_class):
            with patch.object(ingest_main, "StreamPartitioner", mock_partitioner_class):
                with patch.object(ingest_main, "initialize_service", mock_init_service):
                    app = MagicMock(spec=FastAPI)
                    app.state = MagicMock()

                    async with ingest_main.lifespan(app):
                        pass

        # Verify stream was created and assigned
        mock_stream_class.assert_called_once()
        assert app.state.stream == mock_stream

    @pytest.mark.asyncio
    async def test_lifespan_startup_initializes_partitioner(
        self,
    ) -> None:
        """Test lifespan initializes stream partitioner on startup."""
        mock_stream = MagicMock()
        mock_stream.close = AsyncMock()
        mock_stream_class = MagicMock(return_value=mock_stream)

        mock_partitioner = MagicMock()
        mock_partitioner_class = MagicMock(return_value=mock_partitioner)

        mock_init_service = MagicMock()

        with patch.object(ingest_main, "RedisStream", mock_stream_class):
            with patch.object(ingest_main, "StreamPartitioner", mock_partitioner_class):
                with patch.object(ingest_main, "initialize_service", mock_init_service):
                    app = MagicMock(spec=FastAPI)
                    app.state = MagicMock()

                    async with ingest_main.lifespan(app):
                        pass

        # Verify partitioner was created and assigned
        mock_partitioner_class.assert_called_once()
        assert app.state.partitioner == mock_partitioner

    @pytest.mark.asyncio
    async def test_lifespan_startup_calls_initialize_service(
        self,
    ) -> None:
        """Test lifespan calls initialize_service on startup."""
        mock_stream = MagicMock()
        mock_stream.close = AsyncMock()
        mock_stream_class = MagicMock(return_value=mock_stream)

        mock_partitioner = MagicMock()
        mock_partitioner_class = MagicMock(return_value=mock_partitioner)

        mock_init_service = MagicMock()

        with patch.object(ingest_main, "RedisStream", mock_stream_class):
            with patch.object(ingest_main, "StreamPartitioner", mock_partitioner_class):
                with patch.object(ingest_main, "initialize_service", mock_init_service):
                    app = MagicMock(spec=FastAPI)
                    app.state = MagicMock()

                    async with ingest_main.lifespan(app):
                        pass

        # Verify initialize_service was called with stream and partitioner
        mock_init_service.assert_called_once()
        call_kwargs = mock_init_service.call_args[1]
        assert "stream" in call_kwargs
        assert "partitioner" in call_kwargs

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_closes_stream(
        self,
    ) -> None:
        """Test lifespan closes stream on shutdown."""
        mock_stream = MagicMock()
        mock_stream.close = AsyncMock()
        mock_stream_class = MagicMock(return_value=mock_stream)

        mock_partitioner_class = MagicMock()
        mock_init_service = MagicMock()

        with patch.object(ingest_main, "RedisStream", mock_stream_class):
            with patch.object(ingest_main, "StreamPartitioner", mock_partitioner_class):
                with patch.object(ingest_main, "initialize_service", mock_init_service):
                    app = MagicMock(spec=FastAPI)
                    app.state = MagicMock()

                    async with ingest_main.lifespan(app):
                        pass

        # Verify stream.close was called
        mock_stream.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_lifespan_shutdown_handles_close_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test lifespan handles error during stream close."""
        mock_stream = MagicMock()
        mock_stream.close = AsyncMock(side_effect=Exception("Connection error"))
        mock_stream_class = MagicMock(return_value=mock_stream)

        mock_partitioner_class = MagicMock()
        mock_init_service = MagicMock()

        with patch.object(ingest_main, "RedisStream", mock_stream_class):
            with patch.object(ingest_main, "StreamPartitioner", mock_partitioner_class):
                with patch.object(ingest_main, "initialize_service", mock_init_service):
                    app = MagicMock(spec=FastAPI)
                    app.state = MagicMock()

                    with caplog.at_level(logging.ERROR):
                        async with ingest_main.lifespan(app):
                            pass

        # Verify error was logged
        log_messages = [record.message for record in caplog.records]
        assert any("Error closing Redis connection" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_lifespan_uses_custom_redis_url(
        self,
    ) -> None:
        """Test lifespan uses custom redis_url from app state."""
        mock_stream = MagicMock()
        mock_stream.close = AsyncMock()
        mock_stream_class = MagicMock(return_value=mock_stream)

        mock_partitioner_class = MagicMock()
        mock_init_service = MagicMock()

        with patch.object(ingest_main, "RedisStream", mock_stream_class):
            with patch.object(ingest_main, "StreamPartitioner", mock_partitioner_class):
                with patch.object(ingest_main, "initialize_service", mock_init_service):
                    app = MagicMock(spec=FastAPI)
                    app.state = MagicMock()
                    app.state.redis_url = "redis://custom:6379"

                    async with ingest_main.lifespan(app):
                        pass

        # Verify RedisStream was called with custom URL
        mock_stream_class.assert_called_once_with(url="redis://custom:6379")

    @pytest.mark.asyncio
    async def test_lifespan_uses_custom_num_partitions(
        self,
    ) -> None:
        """Test lifespan uses custom num_partitions from app state."""
        mock_stream = MagicMock()
        mock_stream.close = AsyncMock()
        mock_stream_class = MagicMock(return_value=mock_stream)

        mock_partitioner_class = MagicMock()
        mock_init_service = MagicMock()

        with patch.object(ingest_main, "RedisStream", mock_stream_class):
            with patch.object(ingest_main, "StreamPartitioner", mock_partitioner_class):
                with patch.object(ingest_main, "initialize_service", mock_init_service):
                    app = MagicMock(spec=FastAPI)
                    app.state = MagicMock()
                    app.state.num_partitions = 5

                    async with ingest_main.lifespan(app):
                        pass

        # Verify StreamPartitioner was called with custom partitions
        mock_partitioner_class.assert_called_once_with(num_partitions=5)


class TestMain:
    """Test main entry point function."""

    def test_main_returns_zero_on_success(
        self,
    ) -> None:
        """Test main returns 0 on successful execution."""
        mock_uvicorn_run = MagicMock()
        mock_create_app = MagicMock()
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        with patch.object(ingest_main.uvicorn, "run", mock_uvicorn_run):
            with patch.object(ingest_main, "create_app", mock_create_app):
                with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379"}):
                    exit_code = ingest_main.main()

        assert exit_code == 0

    def test_main_returns_one_on_missing_redis_url(
        self,
    ) -> None:
        """Test main returns 1 when REDIS_URL is missing."""
        mock_log = MagicMock()

        with patch.object(ingest_main, "_log", mock_log):
            with patch.dict(os.environ, {}, clear=True):
                exit_code = ingest_main.main()

        assert exit_code == 1

    def test_main_returns_one_on_value_error(
        self,
    ) -> None:
        """Test main returns 1 on ValueError."""
        mock_uvicorn_run = MagicMock(side_effect=ValueError("Invalid config"))
        mock_create_app = MagicMock()

        with patch.object(ingest_main.uvicorn, "run", mock_uvicorn_run):
            with patch.object(ingest_main, "create_app", mock_create_app):
                with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379"}):
                    exit_code = ingest_main.main()

        assert exit_code == 1

    def test_main_returns_two_on_connection_error(
        self,
    ) -> None:
        """Test main returns 2 on ConnectionError."""
        error_msg = "Cannot connect to Redis"
        mock_uvicorn_run = MagicMock(side_effect=ConnectionError(error_msg))
        mock_create_app = MagicMock()

        with patch.object(ingest_main.uvicorn, "run", mock_uvicorn_run):
            with patch.object(ingest_main, "create_app", mock_create_app):
                with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379"}):
                    exit_code = ingest_main.main()

        assert exit_code == 2

    def test_main_returns_zero_on_keyboard_interrupt(
        self,
    ) -> None:
        """Test main returns 0 on KeyboardInterrupt."""
        mock_uvicorn_run = MagicMock(side_effect=KeyboardInterrupt())
        mock_create_app = MagicMock()

        with patch.object(ingest_main.uvicorn, "run", mock_uvicorn_run):
            with patch.object(ingest_main, "create_app", mock_create_app):
                with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379"}):
                    exit_code = ingest_main.main()

        assert exit_code == 0

    def test_main_returns_three_on_runtime_error(
        self,
    ) -> None:
        """Test main returns 3 on unexpected exception."""
        mock_uvicorn_run = MagicMock(side_effect=RuntimeError("Unexpected error"))
        mock_create_app = MagicMock()

        with patch.object(ingest_main.uvicorn, "run", mock_uvicorn_run):
            with patch.object(ingest_main, "create_app", mock_create_app):
                with patch.dict(os.environ, {"REDIS_URL": "redis://localhost:6379"}):
                    exit_code = ingest_main.main()

        assert exit_code == 3

    def test_main_uses_environment_variables(
        self,
    ) -> None:
        """Test main uses configuration from environment variables."""
        mock_uvicorn_run = MagicMock()
        mock_create_app = MagicMock()
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        env_vars = {
            "REDIS_URL": "redis://test:6379",
            "INGEST_API_HOST": "127.0.0.1",
            "INGEST_API_PORT": "9000",
            "LOG_LEVEL": "DEBUG",
        }

        with patch.object(ingest_main.uvicorn, "run", mock_uvicorn_run):
            with patch.object(ingest_main, "create_app", mock_create_app):
                with patch.dict(os.environ, env_vars):
                    ingest_main.main()

        # Verify uvicorn.run was called with correct parameters
        mock_uvicorn_run.assert_called_once()
        call_kwargs = mock_uvicorn_run.call_args[1]
        assert call_kwargs["host"] == "127.0.0.1"
        assert call_kwargs["port"] == 9000
        assert call_kwargs["log_level"] == "debug"

    def test_main_stores_redis_url_in_app_state(
        self,
    ) -> None:
        """Test main stores redis_url in app.state."""
        mock_uvicorn_run = MagicMock()
        mock_create_app = MagicMock()
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app

        with patch.object(ingest_main.uvicorn, "run", mock_uvicorn_run):
            with patch.object(ingest_main, "create_app", mock_create_app):
                with patch.dict(os.environ, {"REDIS_URL": "redis://custom:6379"}):
                    ingest_main.main()

        assert mock_app.state.redis_url == "redis://custom:6379"


__all__ = ["TestCreateApp", "TestLifespan", "TestMain"]
