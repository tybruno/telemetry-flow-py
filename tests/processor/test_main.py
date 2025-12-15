"""Tests for processor main module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.processor.main import run_worker, main


class TestRunWorker:
    """Tests for run_worker function."""

    @pytest.mark.asyncio
    async def test_run_worker_initializes_components(self) -> None:
        """Test that run_worker initializes all components."""
        with patch("src.processor.main.ProcessorConfig") as mock_config_class, \
             patch("src.processor.main.RedisStream") as mock_stream_class, \
             patch("src.processor.main.TelemetryConsumer") as mock_consumer_class, \
             patch("src.processor.main.TumblingWindowAggregator") as mock_agg_class, \
             patch("src.processor.main.ThresholdDetector") as mock_detector_class, \
             patch("src.processor.main.RedisStore") as mock_store_class, \
             patch("src.processor.main.ConsoleAlerter") as mock_alerter_class, \
             patch("src.processor.main.TelemetryWorker") as mock_worker_class:
            
            # Setup mock config
            mock_config = MagicMock()
            mock_config.window_size_seconds = 60
            mock_config.default_threshold = 80.0
            mock_config.get_stream_name.return_value = "telemetry"
            mock_config.consumer_group = "processors"
            mock_config.consumer_name_prefix = "worker"
            mock_config.max_retries = 3
            mock_config.redis_url = "redis://localhost"
            mock_config.partition_id = None
            mock_config.metric_thresholds = {}
            mock_config_class.return_value = mock_config

            # Setup mock stream
            mock_stream = AsyncMock()
            mock_stream.create_consumer_group = AsyncMock()
            mock_stream.close = AsyncMock()
            mock_stream_class.return_value = mock_stream

            # Setup mock storage
            mock_storage = AsyncMock()
            mock_storage.close = AsyncMock()
            mock_store_class.return_value = mock_storage

            # Setup mock worker
            mock_worker = AsyncMock()
            mock_worker.start = AsyncMock(side_effect=KeyboardInterrupt)
            mock_worker.stop = AsyncMock()
            mock_worker_class.return_value = mock_worker

            # Run the worker
            await run_worker()

            # Verify initialization
            mock_stream_class.assert_called_once()
            mock_consumer_class.assert_called_once()
            mock_agg_class.assert_called_once()
            mock_detector_class.assert_called_once()
            mock_store_class.assert_called_once()
            mock_alerter_class.assert_called_once()
            mock_worker_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_worker_creates_consumer_group(self) -> None:
        """Test that run_worker creates consumer group."""
        with patch("src.processor.main.ProcessorConfig") as mock_config_class, \
             patch("src.processor.main.RedisStream") as mock_stream_class, \
             patch("src.processor.main.TelemetryConsumer"), \
             patch("src.processor.main.TumblingWindowAggregator"), \
             patch("src.processor.main.ThresholdDetector"), \
             patch("src.processor.main.RedisStore") as mock_store_class, \
             patch("src.processor.main.ConsoleAlerter"), \
             patch("src.processor.main.TelemetryWorker") as mock_worker_class:
            
            mock_config = MagicMock()
            mock_config.get_stream_name.return_value = "telemetry"
            mock_config.consumer_group = "processors"
            mock_config.consumer_name_prefix = "worker"
            mock_config.max_retries = 3
            mock_config.redis_url = "redis://localhost"
            mock_config.partition_id = None
            mock_config.window_size_seconds = 60
            mock_config.default_threshold = 80.0
            mock_config.metric_thresholds = {}
            mock_config_class.return_value = mock_config

            mock_stream = AsyncMock()
            mock_stream.create_consumer_group = AsyncMock()
            mock_stream.close = AsyncMock()
            mock_stream_class.return_value = mock_stream

            mock_storage = AsyncMock()
            mock_storage.close = AsyncMock()
            mock_store_class.return_value = mock_storage

            mock_worker = AsyncMock()
            mock_worker.start = AsyncMock(side_effect=KeyboardInterrupt)
            mock_worker.stop = AsyncMock()
            mock_worker_class.return_value = mock_worker

            await run_worker()

            # Verify consumer group creation
            mock_stream.create_consumer_group.assert_called_once_with(
                stream="telemetry",
                group="processors",
                start_id="0"
            )

    @pytest.mark.asyncio
    async def test_run_worker_cleans_up_on_error(self) -> None:
        """Test that run_worker cleans up resources on error."""
        with patch("src.processor.main.ProcessorConfig") as mock_config_class, \
             patch("src.processor.main.RedisStream") as mock_stream_class, \
             patch("src.processor.main.TelemetryConsumer"), \
             patch("src.processor.main.TumblingWindowAggregator"), \
             patch("src.processor.main.ThresholdDetector"), \
             patch("src.processor.main.RedisStore") as mock_store_class, \
             patch("src.processor.main.ConsoleAlerter"), \
             patch("src.processor.main.TelemetryWorker") as mock_worker_class:
            
            mock_config = MagicMock()
            mock_config.get_stream_name.return_value = "telemetry"
            mock_config.consumer_group = "processors"
            mock_config.consumer_name_prefix = "worker"
            mock_config.max_retries = 3
            mock_config.redis_url = "redis://localhost"
            mock_config.partition_id = None
            mock_config.window_size_seconds = 60
            mock_config.default_threshold = 80.0
            mock_config.metric_thresholds = {}
            mock_config_class.return_value = mock_config

            mock_stream = AsyncMock()
            mock_stream.create_consumer_group = AsyncMock()
            mock_stream.close = AsyncMock()
            mock_stream_class.return_value = mock_stream

            mock_storage = AsyncMock()
            mock_storage.close = AsyncMock()
            mock_store_class.return_value = mock_storage

            mock_worker = AsyncMock()
            mock_worker.start = AsyncMock(side_effect=Exception("Worker error"))
            mock_worker.stop = AsyncMock()
            mock_worker_class.return_value = mock_worker

            with pytest.raises(Exception, match="Worker error"):
                await run_worker()

            # Verify cleanup
            mock_worker.stop.assert_called_once()
            mock_storage.close.assert_called_once()
            mock_stream.close.assert_called_once()


class TestMain:
    """Tests for main entry point."""

    def test_main_returns_zero_on_success(self) -> None:
        """Test main returns 0 on successful execution."""
        with patch("src.processor.main.ProcessorConfig") as mock_config_class, \
             patch("src.processor.main.asyncio.run") as mock_run:
            
            mock_config = MagicMock()
            mock_config.validate_config = MagicMock()
            mock_config_class.return_value = mock_config

            result = main()

            assert result == 0
            mock_run.assert_called_once()

    def test_main_returns_one_on_config_error(self) -> None:
        """Test main returns 1 on configuration error."""
        with patch("src.processor.main.ProcessorConfig") as mock_config_class:
            mock_config = MagicMock()
            mock_config.validate_config.side_effect = ValueError("Bad config")
            mock_config_class.return_value = mock_config

            result = main()

            assert result == 1

    def test_main_returns_two_on_connection_error(self) -> None:
        """Test main returns 2 on connection error."""
        with patch("src.processor.main.ProcessorConfig") as mock_config_class, \
             patch("src.processor.main.asyncio.run") as mock_run:
            
            mock_config = MagicMock()
            mock_config.validate_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            mock_run.side_effect = ConnectionError("Redis unavailable")

            result = main()

            assert result == 2

    def test_main_returns_zero_on_keyboard_interrupt(self) -> None:
        """Test main returns 0 on keyboard interrupt."""
        with patch("src.processor.main.ProcessorConfig") as mock_config_class, \
             patch("src.processor.main.asyncio.run") as mock_run:
            
            mock_config = MagicMock()
            mock_config.validate_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            mock_run.side_effect = KeyboardInterrupt()

            result = main()

            assert result == 0

    def test_main_returns_three_on_general_error(self) -> None:
        """Test main returns 3 on general processing error."""
        with patch("src.processor.main.ProcessorConfig") as mock_config_class, \
             patch("src.processor.main.asyncio.run") as mock_run:
            
            mock_config = MagicMock()
            mock_config.validate_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            mock_run.side_effect = RuntimeError("Processing failed")

            result = main()

            assert result == 3

    def test_main_configures_logging(self) -> None:
        """Test main configures logging."""
        with patch("src.processor.main.ProcessorConfig") as mock_config_class, \
             patch("src.processor.main.asyncio.run"), \
             patch("src.processor.main._log.basicConfig") as mock_basic_config:
            
            mock_config = MagicMock()
            mock_config.validate_config = MagicMock()
            mock_config_class.return_value = mock_config

            main()

            mock_basic_config.assert_called_once()
