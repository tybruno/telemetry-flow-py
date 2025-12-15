"""Shared test fixtures for simulator tests."""

import pytest


@pytest.fixture
def mock_ingest_url() -> str:
    """Mock ingest URL for testing.
    
    Returns:
        Mock URL string.
    """
    url = "http://test-ingest:8000"
    return url


@pytest.fixture
def sample_device_id() -> str:
    """Sample device ID for testing.
    
    Returns:
        Device ID string.
    """
    device_id = "router-01"
    return device_id


@pytest.fixture
def sample_interfaces() -> list[str]:
    """Sample interfaces for testing.
    
    Returns:
        List of interface names.
    """
    interfaces = ["eth0", "eth1", "eth2"]
    return interfaces


@pytest.fixture
def sample_metrics() -> list[str]:
    """Sample metrics for testing.
    
    Returns:
        List of metric names.
    """
    metrics = [
        "packet_loss_rate",
        "latency_ms",
        "bandwidth_utilization",
        "error_rate",
    ]
    return metrics


__all__: list[str] = []
