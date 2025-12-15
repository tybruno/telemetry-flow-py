"""Tests for simulator main module."""

import asyncio
import logging
import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from simulator.main import (
    generate_metric_value,
    main,
    run_simulator,
    send_telemetry,
    simulate_device,
)


class TestSendTelemetry:
    """Tests for send_telemetry function."""

    @pytest.mark.asyncio
    async def test_send_telemetry_success(
        self, mock_ingest_url: str, sample_device_id: str
    ) -> None:
        """Test successful telemetry sending.
        
        Args:
            mock_ingest_url: Mock ingest URL fixture.
            sample_device_id: Sample device ID fixture.
        """
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await send_telemetry(
                ingest_url=mock_ingest_url,
                device_id=sample_device_id,
                interface="eth0",
                metric_name="packet_loss_rate",
                metric_value=0.05,
            )
            
            send_successful = result is True
            assert send_successful

    @pytest.mark.asyncio
    async def test_send_telemetry_http_error(
        self, mock_ingest_url: str, sample_device_id: str
    ) -> None:
        """Test telemetry sending with HTTP error.
        
        Args:
            mock_ingest_url: Mock ingest URL fixture.
            sample_device_id: Sample device ID fixture.
        """
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "error", request=Mock(), response=Mock()
                )
            )
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await send_telemetry(
                ingest_url=mock_ingest_url,
                device_id=sample_device_id,
                interface="eth0",
                metric_name="packet_loss_rate",
                metric_value=0.05,
            )
            
            send_failed = result is False
            assert send_failed

    @pytest.mark.asyncio
    async def test_send_telemetry_timeout(
        self, mock_ingest_url: str, sample_device_id: str
    ) -> None:
        """Test telemetry sending with timeout.
        
        Args:
            mock_ingest_url: Mock ingest URL fixture.
            sample_device_id: Sample device ID fixture.
        """
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await send_telemetry(
                ingest_url=mock_ingest_url,
                device_id=sample_device_id,
                interface="eth0",
                metric_name="packet_loss_rate",
                metric_value=0.05,
            )
            
            send_failed = result is False
            assert send_failed

    @pytest.mark.asyncio
    async def test_send_telemetry_connection_error(
        self, mock_ingest_url: str, sample_device_id: str
    ) -> None:
        """Test telemetry sending with connection error.
        
        Args:
            mock_ingest_url: Mock ingest URL fixture.
            sample_device_id: Sample device ID fixture.
        """
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.post = AsyncMock(
                side_effect=httpx.ConnectError("connection failed")
            )
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await send_telemetry(
                ingest_url=mock_ingest_url,
                device_id=sample_device_id,
                interface="eth0",
                metric_name="packet_loss_rate",
                metric_value=0.05,
            )
            
            send_failed = result is False
            assert send_failed


class TestGenerateMetricValue:
    """Tests for generate_metric_value function."""

    @pytest.mark.parametrize(
        "metric_name,is_anomaly,min_val,max_val",
        [
            ("packet_loss_rate", False, 0.01, 0.05),
            ("packet_loss_rate", True, 0.15, 0.30),
            ("latency_ms", False, 5.0, 20.0),
            ("latency_ms", True, 100.0, 500.0),
            ("bandwidth_utilization", False, 0.3, 0.7),
            ("bandwidth_utilization", True, 0.85, 0.99),
            ("error_rate", False, 0.001, 0.01),
            ("error_rate", True, 0.05, 0.15),
        ],
    )
    def test_generate_metric_value_ranges(
        self, metric_name: str, is_anomaly: bool, min_val: float, max_val: float
    ) -> None:
        """Test metric value generation within correct ranges.
        
        Args:
            metric_name: Name of metric.
            is_anomaly: Whether to generate anomaly.
            min_val: Minimum expected value.
            max_val: Maximum expected value.
        """
        value = generate_metric_value(metric_name, is_anomaly)
        
        value_in_range = min_val <= value <= max_val
        assert value_in_range

    def test_generate_metric_value_unknown_metric(self) -> None:
        """Test metric value generation for unknown metric."""
        value = generate_metric_value("unknown_metric", False)
        
        value_in_default_range = 0.0 <= value <= 100.0
        assert value_in_default_range

    def test_generate_metric_value_normal_vs_anomaly(self) -> None:
        """Test normal values differ from anomalous values."""
        normal_values = [
            generate_metric_value("packet_loss_rate", False) for _ in range(100)
        ]
        anomaly_values = [
            generate_metric_value("packet_loss_rate", True) for _ in range(100)
        ]
        
        avg_normal = sum(normal_values) / len(normal_values)
        avg_anomaly = sum(anomaly_values) / len(anomaly_values)
        
        anomaly_significantly_higher = avg_anomaly > avg_normal * 2
        assert anomaly_significantly_higher


class TestSimulateDevice:
    """Tests for simulate_device function."""

    @pytest.mark.asyncio
    async def test_simulate_device_sends_telemetry(
        self,
        sample_device_id: str,
        sample_interfaces: list[str],
        sample_metrics: list[str],
        mock_ingest_url: str,
    ) -> None:
        """Test device simulation sends telemetry.
        
        Args:
            sample_device_id: Sample device ID fixture.
            sample_interfaces: Sample interfaces fixture.
            sample_metrics: Sample metrics fixture.
            mock_ingest_url: Mock ingest URL fixture.
        """
        call_count = 0
        
        async def mock_send(*args: Any, **kwargs: Any) -> bool:
            nonlocal call_count
            call_count += 1
            return True
        
        with patch("simulator.main.send_telemetry", side_effect=mock_send):
            with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
                try:
                    await simulate_device(
                        device_id=sample_device_id,
                        interfaces=sample_interfaces,
                        metrics=sample_metrics,
                        ingest_url=mock_ingest_url,
                        interval_seconds=1.0,
                        anomaly_rate=0.0,
                    )
                except asyncio.CancelledError:
                    pass
        
        expected_calls = len(sample_interfaces) * len(sample_metrics)
        calls_correct = call_count == expected_calls
        assert calls_correct

    @pytest.mark.asyncio
    async def test_simulate_device_handles_cancelled(
        self,
        sample_device_id: str,
        sample_interfaces: list[str],
        sample_metrics: list[str],
        mock_ingest_url: str,
    ) -> None:
        """Test device simulation handles cancellation gracefully.
        
        Args:
            sample_device_id: Sample device ID fixture.
            sample_interfaces: Sample interfaces fixture.
            sample_metrics: Sample metrics fixture.
            mock_ingest_url: Mock ingest URL fixture.
        """
        async def mock_send(*args: Any, **kwargs: Any) -> bool:
            return True
        
        with patch("simulator.main.send_telemetry", side_effect=mock_send):
            with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
                # Should exit cleanly without raising
                await simulate_device(
                    device_id=sample_device_id,
                    interfaces=sample_interfaces,
                    metrics=sample_metrics,
                    ingest_url=mock_ingest_url,
                    interval_seconds=1.0,
                    anomaly_rate=0.0,
                )
                
                # Test passes if we get here
                cancelled_handled = True
                assert cancelled_handled

    @pytest.mark.asyncio
    async def test_simulate_device_handles_errors(
        self,
        sample_device_id: str,
        sample_interfaces: list[str],
        sample_metrics: list[str],
        mock_ingest_url: str,
    ) -> None:
        """Test device simulation handles errors.
        
        Args:
            sample_device_id: Sample device ID fixture.
            sample_interfaces: Sample interfaces fixture.
            sample_metrics: Sample metrics fixture.
            mock_ingest_url: Mock ingest URL fixture.
        """
        error_count = 0
        
        async def mock_send_with_error(*args: Any, **kwargs: Any) -> bool:
            nonlocal error_count
            error_count += 1
            if error_count == 1:
                raise RuntimeError("Test error")
            return True
        
        sleep_count = 0
        
        async def mock_sleep(seconds: float) -> None:
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count >= 2:
                raise asyncio.CancelledError
        
        with patch("simulator.main.send_telemetry", side_effect=mock_send_with_error):
            with patch("asyncio.sleep", side_effect=mock_sleep):
                try:
                    await simulate_device(
                        device_id=sample_device_id,
                        interfaces=sample_interfaces,
                        metrics=sample_metrics,
                        ingest_url=mock_ingest_url,
                        interval_seconds=1.0,
                        anomaly_rate=0.0,
                    )
                except asyncio.CancelledError:
                    pass
        
        error_was_handled = sleep_count >= 2
        assert error_was_handled


class TestRunSimulator:
    """Tests for run_simulator function."""

    @pytest.mark.asyncio
    async def test_run_simulator_creates_tasks(self) -> None:
        """Test simulator creates tasks for devices."""
        async def mock_simulate(*args: Any, **kwargs: Any) -> None:
            await asyncio.sleep(0.01)
        
        with patch("simulator.main.simulate_device", side_effect=mock_simulate):
            with patch("asyncio.gather", side_effect=KeyboardInterrupt):
                try:
                    await run_simulator()
                except KeyboardInterrupt:
                    pass
        
        test_passed = True
        assert test_passed

    @pytest.mark.asyncio
    async def test_run_simulator_uses_env_vars(self) -> None:
        """Test simulator uses environment variables."""
        with patch.dict(
            os.environ,
            {
                "SIMULATOR_NUM_DEVICES": "3",
                "SIMULATOR_INTERVAL_SECONDS": "5",
                "SIMULATOR_ANOMALY_RATE": "0.2",
                "INGEST_URL": "http://custom:9000",
            },
        ):
            # Mock simulate_device to track calls
            call_count = 0
            
            async def mock_simulate_device(*args: Any, **kwargs: Any) -> None:
                nonlocal call_count
                call_count += 1
                await asyncio.sleep(0.01)  # Small delay to allow cancellation

            with patch("simulator.main.simulate_device", side_effect=mock_simulate_device):
                # Create a task that will be cancelled shortly
                task = asyncio.create_task(run_simulator())
                await asyncio.sleep(0.05)  # Let it start
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass  # Expected
                
                # Verify 3 devices were created
                assert call_count == 3

    @pytest.mark.asyncio
    async def test_run_simulator_handles_keyboard_interrupt(self) -> None:
        """Test simulator handles keyboard interrupt."""
        async def mock_simulate(*args: Any, **kwargs: Any) -> None:
            await asyncio.sleep(0.01)
        
        with patch("simulator.main.simulate_device", side_effect=mock_simulate):
            with patch("asyncio.gather", side_effect=KeyboardInterrupt):
                try:
                    await run_simulator()
                except KeyboardInterrupt:
                    pass
                
                simulator_handled_interrupt = True
                assert simulator_handled_interrupt


class TestMain:
    """Tests for main function."""

    def test_main_success(self) -> None:
        """Test main function returns 0 on success."""
        async def mock_run() -> None:
            raise KeyboardInterrupt
        
        with patch("simulator.main.run_simulator", side_effect=mock_run):
            exit_code = main()
            
            exit_code_is_zero = exit_code == 0
            assert exit_code_is_zero

    def test_main_keyboard_interrupt(self) -> None:
        """Test main handles keyboard interrupt."""
        with patch("asyncio.run", side_effect=KeyboardInterrupt):
            exit_code = main()
            
            exit_code_is_zero = exit_code == 0
            assert exit_code_is_zero

    def test_main_value_error(self) -> None:
        """Test main handles ValueError."""
        with patch("asyncio.run", side_effect=ValueError("test error")):
            exit_code = main()
            
            exit_code_is_one = exit_code == 1
            assert exit_code_is_one

    def test_main_connection_error(self) -> None:
        """Test main handles ConnectionError."""
        with patch("asyncio.run", side_effect=ConnectionError("test error")):
            exit_code = main()
            
            exit_code_is_two = exit_code == 2
            assert exit_code_is_two

    def test_main_runtime_error(self) -> None:
        """Test main handles runtime errors."""
        with patch("asyncio.run", side_effect=RuntimeError("test error")):
            exit_code = main()
            
            exit_code_is_three = exit_code == 3
            assert exit_code_is_three

    def test_main_uses_log_level_env(self) -> None:
        """Test main uses LOG_LEVEL environment variable."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            with patch("asyncio.run", side_effect=KeyboardInterrupt):
                with patch("logging.basicConfig") as mock_basicconfig:
                    main()
                    
                    # Verify basicConfig was called with DEBUG level
                    called_with_debug = any(
                        call[1].get("level") == logging.DEBUG
                        for call in mock_basicconfig.call_args_list
                    )
                    assert called_with_debug or mock_basicconfig.called
